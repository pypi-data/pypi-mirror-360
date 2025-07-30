r"""Spectrometer drivers for Zurich Instruments devices.

Currently implemented are drivers for the DAQ and the scope module of
the MFLI.

.. note::

    Tested with LabOne version 24.10

Examples
--------
Start up a session and connect the device::

    from zhinst import toolkit

    session = toolkit.Session('localhost')
    device = session.connect_device('dev5247', interface='1gbe')

Set up :class:`~python_spectrometer.core.Spectrometer`
instances once using the DAQ module and once using the Scope module::

    from tempfile import mkdtemp
    from python_spectrometer import Spectrometer
    from python_spectrometer.daq import zurich_instruments

    spect_daq = Spectrometer(
        zurich_instruments.ZurichInstrumentsMFLIDAQ(session, device),
        plot_absolute_frequencies=False,
        savepath=mkdtemp()
    )
    spect_scope = Spectrometer(
        zurich_instruments.ZurichInstrumentsMFLIScope(session, device),
        savepath=mkdtemp()
    )

Compare their results::

    spect_daq.take(n_pts=2**14, fs=14.6e3, freq=500)
    spect_scope.take(n_pts=2**14, fs=14.6e3)

The DAQ spectrum should show a peak at :math:`f=-500\,\mathrm{Hz}`,
corresponding to the oscillator frequency. This is the shifted 0 Hz
peak of the instrument's $1/f$ noise.

Use ``procfn`` to compute the phase noise spectrum using the DAQ module::

    spect_daq.procfn = lambda x, **_: np.angle(x)
    spect_daq.processed_unit = 'rad'
    spect_daq.drop('all')
    spect_daq.take()

"""
from __future__ import annotations

import dataclasses
import logging
import sys
import time
import warnings
from abc import ABC
from collections.abc import Mapping
from typing import Any, Dict, Optional, Type

import numpy as np
from packaging import version
from qutil.domains import DiscreteInterval, ExponentialDiscreteInterval
from scipy.special import gamma
from zhinst import toolkit
from zhinst.core.errors import SampleLossError
from zhinst.toolkit.exceptions import ToolkitError

from .base import DAQ, AcquisitionGenerator
from .settings import DAQSettings

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated
try:
    from numpy.typing import NDArray
except ImportError:
    from numpy import ndarray as NDArray
try:
    from typing import TypeVar
except ImportError:
    from typing_extensions import TypeVar

if version.parse(toolkit.__version__) < version.parse('0.5.0'):
    raise ImportError('This DAQ requires zhinst-toolkit >= 0.5.0. '
                      "You can install it by running 'pip install zhinst-toolkit>=0.5.0'.")

logger = logging.getLogger(__name__)

ZhinstDeviceT = TypeVar('ZhinstDeviceT', bound=toolkit.driver.devices.base.BaseInstrument)


@dataclasses.dataclass
class _ZurichInstrumentsDevice(DAQ, ABC):
    session: toolkit.session.Session
    """A :class:`zhinst_toolkit:zhinst.toolkit.session.Session`
    session to manage devices."""
    device: str | ZhinstDeviceT
    """Either a serial string, e.g., 'dev5247', or a toolkit
    :class:`zhinst_toolkit:zhinst.toolkit.driver.devices.base.BaseInstrument`
    device object representing the MFLI."""

    def __post_init__(self):
        if isinstance(self.device, str):
            self.device = self.session.connect_device(self.device)

        assert 'LI' in self.device.device_type
        try:
            self.device.check_compatibility()
        except ToolkitError as e:
            warnings.warn(f'Labone software stack not compatible. Continue at your own risk: {e}',
                          RuntimeWarning, stacklevel=2)


@dataclasses.dataclass
class ZurichInstrumentsMFLIDAQ(_ZurichInstrumentsDevice):
    """Use the DAQ module to acquire spectra of demodulated data.

    The data returned is a complex sum of in-phase and quadrature
    components, X + iY, and therefore the resulting spectrum is two-
    sided.

    Parameters
    ----------
    session : toolkit.session.Session
        A zhinst session to manage devices.
    device : Union[str, toolkit.driver.devices.base.BaseInstrument]
        Either a serial string, e.g., 'dev5247', or a toolkit device
        object representing the MFLI.
    demod : int, optional
        The demodulator to use. The default is 0.
    osc : int, optional
        The oscillator to use. The default is 0.

    See Also
    --------
    :class:`ZurichInstrumentsMFLIScope` :
        Acquisition using the scope module, meaning data is acquired
        directly from the device's ADC (before being demodulated).

    """
    DTYPE = np.complexfloating

    demod: int = 0
    """The demodulator to use. The default is 0."""
    osc: int = 0
    """The oscillator to use. The default is 0."""

    def __post_init__(self):
        self.daq_module = self.session.modules.daq
        self.daq_module.device(self.device)

        # While it might look like one could just subscribe to the node string, this will fail
        # silently, so we must subscribe to the actual node
        self.sample_nodes = [
            self.device.demods[self.demod].sample.x,
            self.device.demods[self.demod].sample.y
        ]

    @property
    def DAQSettings(self) -> type[DAQSettings]:
        class MFLIDAQSettings(DAQSettings):
            CLOCKBASE = self.device.clockbase()
            # TODO: always the same for each instrument?
            ALLOWED_FS = ExponentialDiscreteInterval(-23, 0, base=2, prefactor=CLOCKBASE / 70)
            DEFAULT_FS = CLOCKBASE / 70 / 2**6

        return MFLIDAQSettings

    def setup(self, filter_order: int | None = None, freq: float = 50,
              **settings: Mapping) -> dict[str, Any]:
        r"""Sets up the daq module to acquire time series data.

        See [1]_ for information on lock-in measurements.

        Parameters
        ----------
        filter_order : int, optional
            The filter order. Not changed if not given.
        freq : float, optional
            The demodulation (local oscillator) frequency. The default
            is 50. You can control if physical frequencies or
            downconverted frequencies are plotted in the spectrometer
            by setting
            :attr:`~python_spectrometer.Spectrometer.plot_absolute_frequencies`.

            .. note::

                Other frequency settings such as ``f_max`` will be
                referenced to ``freq``, meaning for instance if
                ``freq = 10e3, f_max = 2e3``, the spectrum will have a
                bandwidth of ``[8e3, 12e3]``.
        **settings : Mapping
            Additional settings for data acquisition.

        Notes
        -----
        The demodulator 3 dB bandwidth is chosen as $f_\text{max}$. The
        noise-equivalent power (NEP) bandwidth is related to the time
        constant of the RC filter by

        .. math::

            \tau = \frac{\Gamma\left(n - \frac{1}{2}\right)}
                        {4\sqrt{\pi}f_\mathrm{NEP}\Gamma(n)},

        where :math:`n` is the filter order. By default, it is set to
        ``fs/4``.

        Raises
        ------
        RuntimeError :
            If settings are incompatible with the hardware.

        Returns
        -------
        settings : dict
            A consistent set of DAQ settings.

        References
        ----------
        .. [1] https://www.zhinst.com/europe/en/resources/principles-of-lock-in-detection

        """
        settings = self.DAQSettings(freq=freq, **settings)

        if 'bandwidth' in settings:
            warnings.warn('The bandwidth parameter has been replaced by f_max',
                          DeprecationWarning)

        if 'f_max' not in settings:
            settings.f_max = settings.fs / 4

        if filter_order is not None:
            self.device.demods[self.demod].order(int(filter_order))

        settings = settings.to_consistent_dict()

        # BW 3dB = √(2^(1/n) - 1) / 2πτ
        # BW NEP = Γ(n - 1/2) / 4τ √(π)Γ(n)
        n = self.device.demods[self.demod].order()
        tc = gamma(n - 0.5) / (4 * settings['f_max'] * np.sqrt(np.pi) * gamma(n))

        # Do not use context manager here because somehow settings can get lost
        # with device.set_transaction():
        self.device.oscs[self.osc].freq(freq)
        self.device.demods[self.demod].rate(settings['fs'])
        self.device.demods[self.demod].timeconstant(tc)

        # Update settings with device parameters. Do this before evaluating settings.n_pts below,
        # otherwise fs is constrained.
        settings['bandwidth'] = (
            gamma(n - 0.5)
            / (4 * self.device.demods[self.demod].timeconstant() * np.sqrt(np.pi) * gamma(n))
        )
        settings['filter_order'] = n

        assert np.allclose(settings['fs'], self.device.demods[self.demod].rate())

        self.daq_module.type(0)  # continuous acquisition (trigger off)
        self.daq_module.endless(1)  # continous triggering
        self.daq_module.bandwidth(0)  # no filter on trigger signal

        self.daq_module.grid.mode(4)  # 4: exact, 2: linear interpolation
        self.daq_module.grid.direction(0)  # forward
        self.daq_module.grid.overwrite(0)  # multiple data chunks returned
        self.daq_module.grid.waterfall(0)  # data from newest trigger event always in row 0
        self.daq_module.grid.rowrepetition(1)  # row-wise repetition off
        self.daq_module.grid.rows(1)  # number of rows in the grid
        self.daq_module.grid.cols(settings['n_pts'])  # number of points per row

        self.daq_module.unsubscribe('*')
        for node in self.sample_nodes:
            self.daq_module.subscribe(node)

        logger.debug(f'ZurichInstrumentsMFLIDAQ:setup: actual settings at exit are:\n{settings}')
        return settings

    def acquire(self, *, n_avg: int, **settings) -> AcquisitionGenerator[DTYPE]:
        """Executes a measurement and yields the resulting timetrace."""
        # Clear all data from server for good measure
        self.daq_module.finish()
        self.daq_module.read()
        # arm the acquisition
        self.daq_module.execute()
        # Enable data transfer
        self.device.demods[self.demod].enable(1)
        # make sure we're ready. Also needed to update daq_module.duration()
        self.session.sync()

        trigger_timeout = max(1.5 * self.daq_module.duration(), 2)
        trigger_start = time.perf_counter()

        logger.debug(f'Trigger timeout is {trigger_timeout:.2g}s.')

        while (trigger_time := time.perf_counter() - trigger_start) < trigger_timeout:
            time.sleep(20e-3)
            data = self.daq_module.read(raw=False, clk_rate=self.DAQSettings.CLOCKBASE)
            if '/triggered' in data and data['/triggered'][0] == 1:
                break
        else:
            raise TimeoutError('Timeout during wait for trigger')

        logger.debug(f'Trigger time was {trigger_time:.2g}s.')

        acquisition_timeout = trigger_timeout
        yielded_records = 0
        data = []
        for record in range(n_avg):
            acquisition_start = time.perf_counter()
            while len(data) <= yielded_records:
                if (
                        (acquisition_time := (time.perf_counter() - acquisition_start))
                        > acquisition_timeout
                ):
                    raise TimeoutError(f'Timeout during acquisition of record {record}')

                # If we don't sleep here, the calls to the zhinst api are too frequent for the
                # event loop in the main thread to spin up, leading to a frozen figure during
                # acquisition even if this function is run in a thread.
                time.sleep(20e-3)

                new_data = self.daq_module.read(raw=True, clk_rate=self.DAQSettings.CLOCKBASE)
                # read() might return a non-empty dict even if no new data has arrived. Make sure
                if all(node in new_data for node in self.sample_nodes):
                    # convert dict of list to list of dicts to be compatible with Spectrometer
                    new_records = len(new_data[self.sample_nodes[0]])
                    for rec in range(new_records):
                        data.append({str(node): new_data[node][rec] for node in self.sample_nodes})
                        if any(not np.isfinite(d['value']).all() for d in data[-1].values()):
                            raise SampleLossError('Detected non-finite values in record '
                                                  f'{len(data)}')

                    logger.info(f'Fetched {new_records} new records.')
                    logger.info(f'Acquisition time for records {record}--{record + new_records} '
                                f'was {acquisition_time}s.')

            logger.info(f'Yielding record {record}.')
            yielded_records += 1
            yield sum(data[record][str(node)].pop('value').squeeze() * unit
                      for unit, node in zip([1, 1j], self.sample_nodes))

        self.daq_module.finish()
        # Return all metadata that was acquired
        return data[:n_avg]


@dataclasses.dataclass
class ZurichInstrumentsMFLIScope(_ZurichInstrumentsDevice):
    """Use the Scope module to acquire spectra of ADC data.

    .. note::

        The scope module can only acquire 16384 samples at a time. If
        you need a higher resolution, use the DAQ module.

    Parameters
    ----------
    session : toolkit.session.Session
        A zhinst session to manage devices.
    device : Union[str, toolkit.driver.devices.base.BaseInstrument]
        Either a serial string, e.g., 'dev5247', or a toolkit device
        object representing the MFLI.
    scope : int, optional
        The scope channel to use. The default is 0.

    See Also
    --------
    :func:`MFLI_daq` :
        Acquisition using the DAQ module, meaning data is acquired
        after it has been demodulated.

    """
    scope: int = 0
    """The scope channel to use. The default is 0."""

    def __post_init__(self):
        self.scope_module = self.session.modules.scope

    @staticmethod
    def check_scope_record_flags(scope_records):
        """
        Loop over all records and print a warning to the console if an error bit in
        flags has been set.

        From https://docs.zhinst.com/zhinst-toolkit/en/latest/examples/scope_module.html
        """
        num_records = len(scope_records)
        for index, record in enumerate(scope_records):
            record_idx = f"{index}/{num_records}"
            record_flags = record[0]["flags"]
            logger.debug(f'Record {index} has flags {record_flags}.')
            if record_flags & 1:
                print(f"Warning: Scope record {record_idx} flag indicates dataloss.")
            if record_flags & 2:
                print(f"Warning: Scope record {record_idx} indicates missed trigger.")
            if record_flags & 4:
                print(f"Warning: Scope record {record_idx} indicates transfer failure"
                      "(corrupt data).")

            totalsamples = record[0]["totalsamples"]
            for wave in record[0]["wave"]:
                # Check that the wave in each scope channel contains
                # the expected number of samples.
                assert (
                        len(wave) == totalsamples
                ), f"Scope record {index}/{num_records} size does not match totalsamples."

    @property
    def DAQSettings(self) -> type[DAQSettings]:
        class MFLIScopeSettings(DAQSettings):
            CLOCKBASE = self.device.clockbase()
            # TODO: always the same for each instrument?
            ALLOWED_N_PTS = DiscreteInterval(2 ** 12, 2 ** 14, precision=DAQSettings.PRECISION)
            ALLOWED_FS = ExponentialDiscreteInterval(-16, 0, prefactor=CLOCKBASE, base=2,
                                                     precision=DAQSettings.PRECISION)
            DEFAULT_FS = CLOCKBASE / 2 ** 8

        return MFLIScopeSettings

    def setup(self, **settings: Mapping) -> dict[str, Any]:
        r"""Sets up the scope module to acquire time series data.

        Raises
        ------
        RuntimeError
            If settings are incompatible with the hardware.

        Returns
        -------
        settings : dict
            A consistent set of DAQ settings.

        """
        settings = self.DAQSettings(**settings).to_consistent_dict()

        with self.device.set_transaction():
            self.device.scopes[self.scope].channel(1)  # only channel 1 active
            self.device.scopes[self.scope].channels[0].bwlimit(1)  # avoids aliasing
            self.device.scopes[self.scope].length(settings['n_pts'])
            self.device.scopes[self.scope].time(np.log2(self.DAQSettings.CLOCKBASE
                                                        / settings['fs']))
            self.device.scopes[self.scope].single(0)  # continuous acquisition
            self.device.scopes[self.scope].trigenable(0)
            self.device.scopes[self.scope].trigholdoff(0.050)
            self.device.scopes[self.scope].segments.enable(0)  # requires DIG option

        assert settings['n_pts'] == self.device.scopes[0].length()
        assert settings['fs'] == self.DAQSettings.CLOCKBASE / 2 ** self.device.scopes[0].time()

        self.scope_module.mode(1)  # timetrace (scaled).
        self.scope_module.averager.enable(0)  # no internal averaging (we do this ourselves)
        self.scope_module.unsubscribe('*')
        self.scope_module.subscribe(self.device.scopes[self.scope].wave)

        logger.debug(f'ZurichInstrumentsMFLIScope:setup: actual settings at exit are:\n{settings}')
        return settings

    def acquire(self, *, n_avg: int, **_) -> AcquisitionGenerator[DAQ.DTYPE]:
        """Executes a measurement and yields the resulting timetrace."""
        # Set the number of outer averages
        self.scope_module.historylength(1)
        # Clear all data from server for good measure
        self.scope_module.finish()
        self.scope_module.read()
        # arm the acquisition
        self.scope_module.execute()
        # Enable data transfer
        self.device.scopes[self.scope].enable(1)
        # make sure we're ready
        self.session.sync()

        duration = (self.device.scopes[0].length()
                    / (self.DAQSettings.CLOCKBASE / 2 ** self.device.scopes[0].time()))
        acquisition_timeout = max(1.5 * duration, 30)

        logger.debug(f'Acquisition timeout is {acquisition_timeout:.2g}s.')

        yielded_records = 0
        data = []
        for record in range(n_avg):
            acquisition_start = time.perf_counter()
            while (fetched_records := len(data)) <= yielded_records:
                if (
                        (acquisition_time := (time.perf_counter() - acquisition_start))
                        > acquisition_timeout
                ):
                    raise TimeoutError(f'Timeout during acquisition of record {record}')

                # If we don't sleep here, the calls to the zhinst api are too frequent for the
                # event loop in the main thread to spin up, leading to a frozen figure during
                # acquisition even if this function is run in a thread.
                time.sleep(20e-3)

                if new_records := (self.scope_module.records() - fetched_records):
                    # new records acquired, fetch and check for errors.
                    data.extend(self.scope_module.read()[self.device.scopes[self.scope].wave])
                    self.check_scope_record_flags(data[-new_records:])

                    logger.info(f'Fetched {new_records} new records.')
                    logger.info(f'Acquisition time for records {record}--{record + new_records} '
                                f'was {acquisition_time}s.')

            logger.info(f'Yielding record {record}.')
            yielded_records += 1
            yield data[record][self.scope].pop('wave').squeeze()

        self.scope_module.finish()
        # Return all metadata that was acquired
        return data[:n_avg]



@deprecated("Use ZurichInstrumentsMFLIDAQ instead")
class MFLI_daq(ZurichInstrumentsMFLIDAQ):
    ...


@deprecated("Use ZurichInstrumentsMFLIScope instead")
class MFLI_scope(ZurichInstrumentsMFLIScope):
    ...
