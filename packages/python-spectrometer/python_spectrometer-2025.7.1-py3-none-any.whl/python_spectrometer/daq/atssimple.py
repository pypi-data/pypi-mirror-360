"""Use atssimple to take spectra using Alazar cards.

Examples
--------
Set up and take a spectrum::

    from python_spectrometer import daq, Spectrometer
    from atssimple import atsapi

    board = atsapi.Board(systemId=1, boardId=1)

    # Configure Card according to ATSUserGuide
    samples_per_sec = 125000000.0
    board.setCaptureClock(
        atsapi.INTERNAL_CLOCK,
        atsapi.SAMPLE_RATE_125MSPS,
        atsapi.CLOCK_EDGE_RISING,
        0,
    )
    board.inputControlEx(
        atsapi.CHANNEL_A,
        atsapi.DC_COUPLING,
        atsapi.INPUT_RANGE_PM_1_V,
        atsapi.IMPEDANCE_50_OHM,
    )
    triggerDelay_sec = 0
    triggerDelay_samples = int(triggerDelay_sec * samples_per_sec + 0.5)
    board.setTriggerDelay(triggerDelay_samples)

    # Acquire
    spect = Spectrometer(daq.atssimple.AlazarATS9xx0(board, atsapi.CHANNEL_A,
                         trigger_callback="software"))
    spect.take(fs=1e6, input_range=atsapi.INPUT_RANGE_PM_1_V)

"""

from __future__ import annotations

import dataclasses
import time
from typing import Callable, Literal, Type

import numpy as np
from qutil.domains import ReciprocalDiscreteInterval
from qutil.functools import cached_property

from .base import DAQ, AcquisitionGenerator
from .settings import DAQSettings

try:
    from numpy.typing import NDArray
except ImportError:
    from numpy import array as NDArray

try:
    from atssimple import ATSSimpleCard, acquire_downsample_windows, atsapi
except ImportError as e:
    raise RuntimeError('This DAQ requires the atssimple library. Clone it from '
                       'https://git-ce.rwth-aachen.de/qutech/lab_software/atssimple/') from e


@dataclasses.dataclass
class AlazarATS9xx0(DAQ):
    board: atsapi.Board
    """The ``atssimple.atsapi.Board`` object."""
    hardware_channel: int
    """The Alazar channel to use for acquisition as an integer."""
    trigger_callback: Literal["software"] | None | Callable[[], None] = "software"
    """Trigger mechanism.

    - If software / callable: The alazar card is triggered directly or a
      callable is called on acquisition.
    - If None: No trigger is set, the user should configure the card for
      hardware triggering.
    """

    def __post_init__(self):
        # Create an atssimple card handle to allow for software triggering
        self.card = ATSSimpleCard(
            acquisition_function=acquire_downsample_windows,
            board_ids=(self.board.systemId, self.board.boardId),
        )

        if not self.hardware_channel in (
            atsapi.CHANNEL_A,
            atsapi.CHANNEL_B,
            atsapi.CHANNEL_C,
            atsapi.CHANNEL_D,
        ):
            raise ValueError("Invalid channel!")
        if self.trigger_callback == "software":
            self.trigger_callback = self.card.trigger
        elif not callable(self.trigger_callback) and self.trigger_callback is not None:
            raise ValueError("trigger_callback should be 'software', None, or callable")

        self.default_capture_clock_config = {
            "source": atsapi.INTERNAL_CLOCK,
            "rate": atsapi.SAMPLE_RATE_125MSPS,
            "edge": atsapi.CLOCK_EDGE_RISING,
            "decimation": 0,
        }

    @cached_property
    def DAQSettings(self) -> type[DAQSettings]:
        class AlazarDAQSettings(DAQSettings):
            range_map = {
                atsapi.INPUT_RANGE_PM_20_MV: 20e-03,
                atsapi.INPUT_RANGE_PM_40_MV: 40e-3,
                atsapi.INPUT_RANGE_PM_50_MV: 50e-3,
                atsapi.INPUT_RANGE_PM_80_MV: 80e-3,
                atsapi.INPUT_RANGE_PM_100_MV: 100e-3,
                atsapi.INPUT_RANGE_PM_200_MV: 200e-3,
                atsapi.INPUT_RANGE_PM_400_MV: 400e-3,
                atsapi.INPUT_RANGE_PM_500_MV: 500e-3,
                atsapi.INPUT_RANGE_PM_800_MV: 800e-3,
                atsapi.INPUT_RANGE_PM_1_V: 1,
                atsapi.INPUT_RANGE_PM_2_V: 2,
                atsapi.INPUT_RANGE_PM_4_V: 4,
                atsapi.INPUT_RANGE_PM_5_V: 5,
            }

            sample_rate_map = {
                atsapi.SAMPLE_RATE_100MSPS: 100e06,
                atsapi.SAMPLE_RATE_125MSPS: 125e06,
                atsapi.SAMPLE_RATE_1000MSPS: 1000e06,
                atsapi.SAMPLE_RATE_1800MSPS: 1800e06,
            }

            def _get_numeric_sample_rate(self):
                numeric_sample_rate = self.sample_rate_map.get(
                    self["capture_clock_config"]["rate"]
                )
                if numeric_sample_rate is None:
                    raise ValueError("Invalid sample rate!")

                return numeric_sample_rate

            @property
            def ALLOWED_FS(self) -> ReciprocalDiscreteInterval:
                return ReciprocalDiscreteInterval(
                    numerator=self._get_numeric_sample_rate(), precision=self.PRECISION
                )

            def _validate_input_range(self, input_range):
                if str(input_range) not in self.range_map.keys():
                    raise ValueError("Invalid input range!")

        return AlazarDAQSettings

    def setup(
        self,
        fs: float = 100e6,
        capture_clock_config: dict | None = None,
        input_range: int = atsapi.INPUT_RANGE_PM_1_V,
        **settings,
    ):
        settings = self.DAQSettings(
            fs=fs,
            capture_clock_config=capture_clock_config
            or self.default_capture_clock_config,
            input_range=input_range,
            **settings,
        )

        # Amplitude of the input range
        settings["numeric_input_range"] = settings.range_map[settings["input_range"]]
        # Base sample rate of the alazar card.
        settings["hardware_sample_rate"] = settings.ALLOWED_FS.numerator

        # Make settings consistent
        settings = settings.to_consistent_dict()

        # Number of samples averaged per acquired point
        settings["averaged_samples"] = round(
            settings["hardware_sample_rate"] / settings["fs"]
        )

        self.board.setCaptureClock(**settings["capture_clock_config"])

        self.board.inputControlEx(
            self.hardware_channel,
            atsapi.DC_COUPLING,
            settings["input_range"],
            atsapi.IMPEDANCE_50_OHM,
        )

        if self.trigger_callback == "software":
            self.card.prepare_for_software_trigger()

        return settings

    def acquire(
        self,
        *,
        n_avg: int,
        **settings,
    ) -> AcquisitionGenerator[DAQ.DTYPE]:

        sample_windows = np.full(settings["n_pts"], settings["averaged_samples"])

        for _ in range(n_avg):
            time.sleep(0.05)

            self.card.start_acquisition(
                downsample_windows=sample_windows,
                return_samples_in_seconds=True,
                channel_mask=self.hardware_channel,
                samples_per_second=settings["hardware_sample_rate"],
                voltage_range=settings["numeric_input_range"],
            )

            if self.trigger_callback is not None:
                time.sleep(0.1)
                self.trigger_callback()

            result, samples = self.card.get_results()

            yield result[0]
