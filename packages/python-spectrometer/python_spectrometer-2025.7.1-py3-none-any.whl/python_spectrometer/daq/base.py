from __future__ import annotations

import abc
import sys
import warnings
from abc import ABC
from collections.abc import Generator
from typing import Any, Dict, Optional, Type

import numpy as np
from qutil.functools import cached_property
from qutil.misc import filter_warnings

from .settings import DAQSettings

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
try:
    from numpy.typing import NDArray
except ImportError:
    from numpy import ndarray as NDArray

AcquisitionGenerator: TypeAlias = Generator[NDArray, None, Optional[dict[str, Any]]]


class DAQ(ABC):
    """Abstract base class for data acquisition drivers.

    The class aims to provide a consistent interface for
    :class:`~python_spectrometer.core.Spectrometer` objects
    to handle data acquisition independent of the detailed workings of
    the device driver. It provides three main interfaces;
    :meth:`setup`, which should configure the hardware for measurement,
    :meth:`acquire`, which should execute said measurement and yield
    data when iterated, and :attr:`DAQSettings`, which can be used to
    implement hardware constraints by subclassing the
    :class:`.DAQSettings` class.
    """
    DTYPE = np.floating
    """The data type yielded by :meth:`acquire`."""

    def __post_init__(self):
        """Run import checks here and other setup steps here."""

    def __iter__(self):
        with filter_warnings(action='error', categroy=DeprecationWarning):
            warnings.warn('Data acquisition not implemented as setup() and acquire() functions '
                          f'anymore, but as the {type(self).__name__} class with methods setup() '
                          'and acquire(). Please use that class (arguments remain the same).',
                          DeprecationWarning, stacklevel=2)

    @cached_property
    def DAQSettings(self) -> type[DAQSettings]:
        """This property can be overridden by subclasses to return a
        customized subclass of :class:`.settings.DAQSettings` that
        accounts for certain hardware constraints.

        See :mod:`.settings` for more information.
        """
        return DAQSettings

    def setup(self, **settings) -> dict[str, Any]:
        """Sets up the data acquisition device for measurement.

        Parameters
        ----------
        **settings
            All configuration settings required to set up and execute
            the measurement, as well as possibly metadata. This method
            may modify the settings for instance if the DAQ constrains
            certain values. The (modified) settings are returned as a
            consistent dictionary, which is then passed on to all other
            processing and acquisition functions such as to the
            psd_estimator. Therefore, it should also include all
            parameters relevant for those functions.

        Returns
        -------
        parsed_settings : dict[str, Any]
            The validated settings.
        """
        return self.DAQSettings(**settings).to_consistent_dict()

    @abc.abstractmethod
    def acquire(self, *, n_avg: int, **settings) -> AcquisitionGenerator[DTYPE]:
        """Returns an iterator that yields data n_avg times.

        This method should execute the measurement and yield a
        timetrace in a 1d-array-like format during each iteration.

        Parameters
        ----------
        n_avg : int
            The number of repetitions, that is, the number of times the
            iterator can be queried for data.
        **settings
            Any other runtime settings required for data acquisition.

        Yields
        ------
        data_buffer : array_like
            One data buffer.

        Returns
        -------
        metadata : Any
            Any metadata about the runtime measurement configuration.

        """
        ...
