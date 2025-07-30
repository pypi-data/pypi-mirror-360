"""Data acquisition drivers for the
:class:`~python_spectrometer.core.Spectrometer` class.

Each submodule contains functionality for different backends, such as
QCoDeS or Zurich Instruments. A 'driver' is implemented as a subclass
of the :class:`~core.DAQ` abstract base class. It has two methods;
first, a :meth:`~core.DAQ.setup()` method that configures the data
acquisition device, and second, an :meth:`~core.DAQ.acquire()` method
that when called yields an array of time-series data.
:meth:`~core.DAQ.acquire()` can optionally return measurement metadata
after the iterator is exhausted.

More explicitly, a driver should look something like this::

    @dataclasses.dataclass
    class MyDAQ(DAQ):
        actual_driver: object

        def __post_init__(self, **instantiation_time_settings):
            ...

        def setup(self, **configuration_settings) -> Mapping:
            ...
            return actual_device_configuration

        def acquire(self, *, n_avg: int, **runtime_settings) -> Iterator[ArrayLike]:
            ...
            for _ in range(n_avg):
                yield data
            return metadata

The :class:`settings.DAQSettings` class provides a way of managing
interdependent settings for data acquisition, with special keywords
being reserved for parameters of the
:func:`~qutil:qutil.signal_processing.real_space.welch` function for spectral
estimation. Optionally, the :class:`~core.DAQ` subclass can define a
:attr:`~core.DAQ.DAQSettings` property that returns a customized subclass
of :class:`~settings.DAQSettings` specifying hardware constraints.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)

del lazy
