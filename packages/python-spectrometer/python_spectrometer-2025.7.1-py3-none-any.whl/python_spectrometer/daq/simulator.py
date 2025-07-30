"""Provides a simulation backend for data acquisition.

The :meth:`DAQ.acquire` method of DAQs in this module accepts a
``delay`` keyword argument which introduces a delay in between yields
to simulate a finite data acquisition time. If True, delays by the
amount of time it would take to actually acquire data with the given
settings; if float delays by the given amount.

Examples
--------
>>> import python_spectrometer as pyspeck
>>> import tempfile
>>> speck = pyspeck.Spectrometer(pyspeck.daq.QoptColoredNoise(),
...                              savepath=tempfile.mkdtemp())
>>> speck.take('a test', fs=10e3)
...
>>> speck.block_until_ready()  # for doctest

Add an artificial time delay to mimick finite data acquisition time:
>>> speck.take('delayed', n_avg=3, delay=True)
...

"""
from __future__ import annotations

import copy
import dataclasses
import inspect
import sys
import time
from collections.abc import Callable
from typing import Literal, Union

import numpy as np
from qutil.functools import partial, wraps
from qutil.math import cexp
from qutil.signal_processing import real_space

from .base import DAQ, AcquisitionGenerator

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated
try:
    from numpy.typing import NDArray
except ImportError:
    from numpy import ndarray as NDArray

try:
    import qopt
except ImportError as e:
    raise ImportError('This simulated DAQ requires qopt. You can install it by running '
                      "'pip install qopt.'") from e


def with_delay(meth):
    """Wraps an acquisition generator to accept the *delay* kwarg."""

    @wraps(meth)
    def wrapped(self, *, delay=False, **settings):
        skip_delay = settings.pop('_skip_delay', False)

        if delay is True:
            delay = settings['n_pts'] / settings['fs']

        it = meth(self, _skip_delay=True, **settings)
        while True:
            tic = time.perf_counter()
            try:
                data = next(it)
            except StopIteration as stop:
                return stop.value
            else:
                if delay and not skip_delay:
                    time.sleep(max(0, delay - (time.perf_counter() - tic)))

                yield data

    # Insert parameter sig
    delay_param = inspect.Parameter('delay', inspect.Parameter.KEYWORD_ONLY, default=True,
                                    annotation=Union[bool, float])

    parameters = list(inspect.signature(meth).parameters.values())
    if parameters[-1].kind is inspect.Parameter.VAR_KEYWORD:
        parameters = parameters[:-1] + [delay_param, parameters[-1]]
    else:
        parameters = parameters + [delay_param]

    wrapped.__signature__ = inspect.signature(wrapped).replace(parameters=parameters)
    return wrapped


class MonochromaticNoise(DAQ):
    """Generate monochromatic sinusoidal noise with random phase.

    This DAQ implementation produces sinusoidal data with a fixed frequency
    but random phase for each acquisition, simulating a simple signal with noise.

    Inherits from the base DAQ class and implements the required acquire method.
    """

    @with_delay
    def acquire(self, *, n_avg: int, fs: float, n_pts: int, A: float = 1, f_0: float = 50,
                **settings) -> AcquisitionGenerator[DAQ.DTYPE]:
        """Generate sinusoidal data with random phase."""

        t = np.arange(0, n_pts / fs, 1 / fs)
        rng = np.random.default_rng()

        for _ in range(n_avg):
            yield np.sin(2 * np.pi * (t * f_0 + rng.random()))


@dataclasses.dataclass
class QoptColoredNoise(DAQ):
    """Simulates noise using :mod:`qopt:qopt`.

    See :class:`~python_spectrometer.core.Spectrometer` for
    more details on usage and
    :class:`~python_spectrometer.daq.settings.DAQSettings`
    for more information on setup parameters.

    Attributes
    ----------
    spectral_density : Callable[[NDArray, ...], NDArray]
        A function that generates the power spectral density for given
        frequencies. Defaults to white noise with scale parameter
        ``S_0``.

    See Also
    --------
    :func:`qopt:qopt.noise.fast_colored_noise`
        For information on the simulation.
    """
    spectral_density: Callable[[NDArray, ...], NDArray] = dataclasses.field(
        default_factory=lambda: QoptColoredNoise.white_noise
    )
    """A callable with signature::

        f(ndarray, **settings) -> ndarray

    that returns the power spectral density for given frequencies.
    Defaults to white noise with scale parameter ``S_0``.
    """

    @staticmethod
    def white_noise(f, S_0: float = 1.0, **_) -> NDArray:
        """White noise power spectral density with amplitude S_0."""
        return np.full_like(f, S_0)

    @with_delay
    def acquire(self, *, n_avg: int, fs: float, n_pts: int,
                **settings) -> AcquisitionGenerator[DAQ.DTYPE]:
        """Executes a measurement and yields the resulting timetrace."""
        for _ in range(n_avg):
            yield qopt.noise.fast_colored_noise(
                partial(
                    settings.get('spectral_density', self.spectral_density),
                    **settings
                ),
                dt=1/fs, n_samples=n_pts, output_shape=()
            )

        # This is the place to return metadata (possibly obtained from the instrument)
        return {'qopt version': qopt.__version__}


class DemodulatorQoptColoredNoise(QoptColoredNoise):
    """Simulates demodulated noisy data for lock-in measurements.

    Extends QoptColoredNoise to demodulate the simulated signal using
    complex IQ-demodulation, similar to a lock-in amplifier. This
    provides a realistic simulation of demodulated signals as would be
    measured in experiments using lock-in amplification techniques.
    """
    DTYPE = np.complexfloating

    @staticmethod
    def demodulate(signal: np.ndarray, IQ: np.ndarray, **settings) -> np.ndarray:
        """Demodulate signal using the provided IQ reference.

        Performs complex demodulation by multiplying the signal with
        the IQ reference and applying an RC filter.

        Parameters
        ----------
        signal :
            Input signal to demodulate
        IQ :
            Complex IQ reference for demodulation
        **settings :
            Settings for RC filter, including filter parameters

        """
        # Don't highpass filter
        settings = copy.copy(settings)
        settings.pop('f_min', None)
        return real_space.RC_filter(signal * IQ, **settings)

    @with_delay
    def acquire(self, *, n_avg: int, freq: float = 50, modulate_signal: bool = False,
                filter_order: int = 1,
                filter_method: Literal['forward', 'forward-backward'] = 'forward-backward',
                **settings) -> AcquisitionGenerator[DTYPE]:
        r"""Simulate demodulated noisy data.

        Generates simulated data and performs IQ demodulation, mimicking
        the behavior of a lock-in amplifier. Can simulate either just
        input noise or noise in the full signal path.

        See [1]_ for an introduction to Lock-in amplification.

        Parameters
        ----------
        n_avg :
            Number of outer averages.
        freq :
            Modulation frequency.
        modulate_signal :
            Add the simulated noise to the modulation signal to mimic
            noise picked up by a Lock-In signal travelling through some
            DUT. Otherwise, mimics the noise at the input of the
            amplifier.

            In other words, simulate a Lock-In output connected to an
            input, or just simulate the input.

            Note that if True, noise is assumed to be additive, that
            is,

            .. math::

                x(t) = s(t) + \delta(t)

            with :math:`s(t)` the output signal and :math:`\delta(t)`
            the noise.
        filter_order :
            RC filter order used to filter the demodulated signal.
        filter_method :
            See :func:`~qutil:qutil.signal_processing.real_space.RC_filter`.

        Yields
        ------
        data :
            Demodulated data in complex IQ-representation.

        References
        ----------
        .. [1] https://www.zhinst.com/europe/en/resources/principles-of-lock-in-detection

        """
        t = np.arange(0, settings['n_pts'] / settings['fs'], 1 / settings['fs'])
        # demodulation by √2 exp(-iωt) (ZI convention)
        IQ = np.sqrt(2) * cexp(-2 * np.pi * freq * t)

        yield from (
            self.demodulate(IQ.real + data if modulate_signal else data, IQ,
                            order=filter_order, method=filter_method, **settings)
            for data in super().acquire(n_avg=n_avg, **settings)
        )

        return {'qopt version': qopt.__version__}


@deprecated("Use QoptColoredNoise instead")
class qopt_colored_noise(QoptColoredNoise):
    ...
