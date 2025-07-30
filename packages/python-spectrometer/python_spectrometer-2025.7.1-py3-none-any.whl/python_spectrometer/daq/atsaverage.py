"""Use atsaverage to take spectra using Alazar cards.

Examples
--------
Set up and take a spectrum::

    from python_spectrometer import daq, Spectrometer
    from tempfile import mkdtemp
    from atsaverage import alazar
    from atsaverage.core import getLocalCard

    card = getLocalCard(1, 1)
    spect = Spectrometer(daq.atsaverage.AlazarATS9xx0(card, 0), savepath=mkdtemp())

    spect.take(fs=1e6, input_range=alazar.InputRangeID.range_100_mV)

"""
from __future__ import annotations

import dataclasses
import string
import time
from typing import Callable, Literal, Type

from qutil.domains import ReciprocalDiscreteInterval
from qutil.functools import cached_property

from .base import DAQ, AcquisitionGenerator
from .settings import DAQSettings

try:
    from numpy.typing import NDArray
except ImportError:
    from numpy import array as NDArray

try:
    from atsaverage.alazar import InputRangeID
    from atsaverage.config2 import (BoardConfiguration, CaptureClockConfiguration,
                                    CaptureClockType, Channel, EngineTriggerConfiguration,
                                    InputConfiguration, SampleRateID, create_scanline_definition)
    from atsaverage.core import AlazarCard
    from atsaverage.masks import PeriodicMask
    from atsaverage.operations import Downsample
except ImportError as e:
    raise RuntimeError('This DAQ requires the atsaverage library. Clone it from '
                       'https://git.rwth-aachen.de/qutech/cpp-atsaverage/') from e


@dataclasses.dataclass
class AlazarATS9xx0(DAQ):
    card: AlazarCard
    """The ``atsaverage.core.AlazarCard`` object."""
    hardware_channel: int | str | Channel
    """The Alazar channel to use for acquisition."""
    trigger_callback: Literal['software'] | None | Callable[[], None] = 'software'
    """Trigger mechanism.

     - If software / callable: The alazar card is triggered directly or
       a callable is called on acquisition.
     - If None: No trigger is set, the user should configure the card
       for hardware triggering.

       .. note::

           Not implemented.

    """

    def __post_init__(self):
        if isinstance(self.hardware_channel, int):
            self.hardware_channel = string.ascii_uppercase[self.hardware_channel]
        if not isinstance(self.hardware_channel, Channel):
            self.hardware_channel = getattr(Channel, self.hardware_channel)
        if self.trigger_callback == 'software':
            self.trigger_callback = self.card.forceTrigger
        elif not callable(self.trigger_callback):
            raise NotImplementedError('Hardware trigger not yet implemented. Please open a PR.')

        self.default_capture_clock_config = CaptureClockConfiguration(
            CaptureClockType.internal_clock,
            SampleRateID.rate_100MSPS
        )

    @cached_property
    def DAQSettings(self) -> type[DAQSettings]:
        class AlazarDAQSettings(DAQSettings):
            @property
            def ALLOWED_FS(self) -> ReciprocalDiscreteInterval:
                return ReciprocalDiscreteInterval(
                    numerator=self['capture_clock_config'].get_numeric_sample_rate(),
                    precision=self.PRECISION
                )

        return AlazarDAQSettings

    def setup(self, fs: float = 100e6,
              capture_clock_config: CaptureClockConfiguration | None = None,
              input_range: InputRangeID = InputRangeID.range_1_V,
              **settings):
        settings = self.DAQSettings(
            fs=fs,
            capture_clock_config=capture_clock_config or self.default_capture_clock_config,
            input_range=input_range,
            **settings
        )

        hardware_sample_rate = settings.ALLOWED_FS.numerator
        # can round since settings.fs is guaranteed to be hardware_sample_rate divided by an int
        averaged_samples = round(hardware_sample_rate / settings.fs)
        assert averaged_samples > 0

        masks = [PeriodicMask("M",
                              begin=0, end=averaged_samples, period=averaged_samples,
                              channel=self.hardware_channel, skip=0, take=settings.n_pts)]
        operations = [Downsample('M', 'M')]
        board_spec = self.card.get_board_spec()

        board_config = BoardConfiguration(
            trigger_engine=EngineTriggerConfiguration.software_trigger(),
            capture_clock_configuration=settings['capture_clock_config'],
            input_configuration=InputConfiguration(self.hardware_channel,
                                                   input_range=settings['input_range'])
        )

        scanline_definition = create_scanline_definition(
            masks=masks,
            operations=operations,
            numeric_sample_rate=hardware_sample_rate,
            board_spec=board_spec,
            raw_data_mask=0,
        )

        self.card.apply_board_configuration(board_config)
        self.card.configureMeasurement(scanline_definition)
        self.card.acquisitionTimeout = settings.get(
            'acquisitionTimeout',  # ms...
            max(1000000, int(2 * 1000 * settings['n_pts'] / settings['fs']))
        )
        self.card.computationTimeout = settings.get('computationTimeout',
                                                    self.card.acquisitionTimeout)
        self.card.triggerTimeout = settings.get('triggerTimeout', self.card.acquisitionTimeout)

        return settings.to_consistent_dict()

    def acquire(self, *, n_avg: int, input_range: InputRangeID,
                **settings) -> AcquisitionGenerator[DAQ.DTYPE]:
        self.card.startAcquisition(n_avg)

        for _ in range(n_avg):
            time.sleep(.05)
            self.trigger_callback()
            result = self.card.extractNextScanline()

            yield result.operationResults['M'].getAsVoltage(input_range)

        return self.card.get_board_spec()
