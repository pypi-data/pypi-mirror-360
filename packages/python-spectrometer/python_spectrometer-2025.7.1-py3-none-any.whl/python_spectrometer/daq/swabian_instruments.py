"""Spectrometer driver for time tags using Swabian Instruments."""
from __future__ import annotations

import dataclasses
import sys
import warnings
from collections.abc import Iterable, Sequence
from typing import Any, Dict

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
    import TimeTagger as tt
except ImportError as e:
    raise RuntimeError('This DAQ requires the TimeTagger python module. Download it at '
                       'https://www.swabianinstruments.com/time-tagger/downloads/') from e


@dataclasses.dataclass
class SwabianInstrumentsTimeTagger(DAQ):
    """Manages data acquisition with a Swabian Instruments TimeTagger.

    This uses the :class:`~TimeTagger:Counter` object to create a stream
    of photon numbers.

    See :class:`~python_spectrometer.core.Spectrometer` for
    more details on usage and
    :class:`~python_spectrometer.daq.settings.DAQSettings`
    for more information on setup parameters.

    Examples
    --------
    Use the rms-normalized output of a TimeTagger tag stream as
    time-series data::

        import atexit, sys, numpy as np
        from python_spectrometer import daq, Spectrometer

        sys.path.append('C:/Program Files/Swabian Instruments/Time Tagger/driver/python')

        import TimeTagger
        tagger = TimeTagger.createTimeTagger()
        tagger.setTriggerLevel(1, 1)  # APDs recommend 1 V
        tagger.setTriggerLevel(2, 1)
        _ = atexit.register(TimeTagger.freeTimeTagger, tagger)

        spect = Spectrometer(daq.swabian_instruments.SwabianInstrumentsTimeTagger(tagger, [1, 2]),
                             raw_unit='cts')

    """
    tagger: tt.TimeTagger = dataclasses.field()
    """The :class:`~TimeTagger:TimeTagger` instance representing the
    hardware device."""
    channel: Sequence[int] | int = 1
    """The channel(s) to read out.

    The counts of all channels are accumulated before they are returned.
    """

    def __post_init__(self):
        if not isinstance(self.channel, Iterable):
            self.channel = [self.channel]
        else:
            self.channel = list(self.channel)

        assert len(self.channel) > 0, 'channel should be sequence of ints'

    def setup(self, **settings) -> dict[str, Any]:
        """Sets up a SI TimeTagger to acquire a timetrace for given parameters."""
        # OOO structure of TimeTagger doesn't allow configuration before
        # all parameters are known, so all we can do is check if params
        # are valid.
        if 'fs' in settings:
            # TimeTagger uses units picoseconds
            settings = self.DAQSettings(settings)
            settings.fs = 1e12 / int(1e12 / settings['fs'])
        return super().setup(**settings)

    def acquire(self, *, n_avg: int, fs: float, n_pts: int,
                **_) -> AcquisitionGenerator[DAQ.DTYPE]:
        """Executes a measurement and yields the resulting timetrace."""
        duration = int(1e12 / fs) * n_pts
        counter = tt.Counter(self.tagger, self.channel, duration / n_pts, n_pts)

        for _ in range(n_avg):
            counter.startFor(duration, clear=True)
            counter.waitUntilFinished(2 * duration)

            data = counter.getDataObject()
            if (mask := data.getOverflowMask()).any():
                warnings.warn(f'Data overflow detected in {mask.sum()} bins', RuntimeWarning)
            if data.dropped_bins:
                warnings.warn(f'{data.dropped_bins} dropped bins detected', RuntimeWarning)
            # Upconvert to 8-bit ints so arithmetic with reasonable count rates does not overflow
            yield data.getData().sum(axis=0).astype('i8')

        return counter.getConfiguration()


@deprecated("Use SwabianInstrumentsTimeTagger instead")
class timetagger(SwabianInstrumentsTimeTagger):
    ...
