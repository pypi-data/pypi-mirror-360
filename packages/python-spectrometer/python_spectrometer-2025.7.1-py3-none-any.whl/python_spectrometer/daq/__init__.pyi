__all__ = ['atsaverage', 'atssimple', 'qcodes', 'simulator', 'swabian_instruments',
           'zurich_instruments', 'AlazarATS9xx0', 'Keysight344xxA', 'NationalInstrumentsUSB6003',
           'SwabianInstrumentsTimeTagger', 'DAQSettings', 'QoptColoredNoise',
           'ZurichInstrumentsMFLIScope', 'ZurichInstrumentsMFLIDAQ']

from . import atsaverage, atssimple, qcodes, simulator, swabian_instruments, zurich_instruments
from .atsaverage import AlazarATS9xx0
from .qcodes import (Keysight344xxA, NationalInstrumentsUSB6003,  # Backwards "compatibility"
                     keysight_344xxA, national_instruments_daq)
from .settings import DAQSettings
from .simulator import QoptColoredNoise, qopt_colored_noise  # Backwards "compatibility"
from .swabian_instruments import (SwabianInstrumentsTimeTagger,  # Backwards "compatibility"
                                  timetagger)
from .zurich_instruments import (MFLI_daq, MFLI_scope,  # Backwards "compatibility"
                                 ZurichInstrumentsMFLIDAQ, ZurichInstrumentsMFLIScope)
