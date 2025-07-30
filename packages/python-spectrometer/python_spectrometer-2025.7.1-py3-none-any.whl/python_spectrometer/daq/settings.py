"""Provides a class that manages interdependent settings.

The class subclasses :class:`python:dict` and therefore behaves mostly like
it. Beyond that however, it tries to ensure consistency of certain
parameters relevant for spectral estimation using Welch's method. These
include for instance the sampling rate fs. Such parameters are
implemented as customized properties
(:class:`.interdependent_daq_property`) und can therefore, in addition
to the usual :meth:`python:object.__getitem__` and
:meth:`python:object.__setitem__`, also be gotten and set using
:meth:`python:object.__getattribute__` and
:meth:`python:object.__setattr__`. For example:

>>> s = DAQSettings()
>>> s['fs'] = 3
>>> s['fs']
3
>>> s.fs = 4
>>> s.fs  # Note that fs is converted to float!
4.0

The difference between the two is that when treated as properties,
their values are automatically validated against other, dependent
properties. For instance, the highest frequency f_max cannot be larger
than fs/2 by virtue of Nyquist's theorem. Hence, if there are
conflicting parameters, the class tries to resolve them by adjusting
one or the other and otherwise raising an error. Alternatively, a
certain parameter might be constrained by hardware limitations. These
can be implemented by subclassing :class:`.DAQSettings` and overriding
the attributes :attr:`.DAQSettings.ALLOWED_FS` etc. There exist custom
types for representing constraints in :mod:`qutil:qutil.domains`.

The method :meth:`.DAQSettings.to_consistent_dict` resolves all
dictionary items into a :class:`dict` dictionary which contains all
interdependent parameters validated for consistency.

Internally, interdependent parameters are first cast to a value allowed
by their :class:`qutil:~qutil.domains.Domain` (which implements
constraints both by hardware and other parameters) and then to the
correct type. Finally, other parameters that depend on it are tried to
be adjusted if necessary.

"""
from __future__ import annotations

import builtins
import inspect
import numbers
import platform
import textwrap
import warnings
from collections import ChainMap
from copy import copy
from math import ceil, floor, inf, isinf
from typing import Any, Callable, Dict, Tuple, TypeVar

from numpy import finfo
from packaging import version
from qutil.domains import BoundedSet, ContinuousInterval, DiscreteInterval, Domain
from qutil.functools import wraps

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_RealT = TypeVar("_RealT", bound=numbers.Real)
_IntDomainT = TypeVar("_IntDomainT", bound=Domain[int])
_FloatDomainT = TypeVar("_FloatDomainT", bound=Domain[float])

_doc_ = {
    'fs': "float.\n\tThe sampling rate. Default: ``2*f_max`` or :attr:`DEFAULT_FS`.",
    'df': "float.\n\t" r"The frequency spacing :math:`\Delta f`. If given, supersedes "
          ":attr:`f_min` for computing the total duration of the record. Default: :attr:`f_min` "
          "or :attr:`DEFAULT_DF`.",
    'f_max': "float.\n\tThe maximum frequency displayed. Also used for filters. Defaults to half "
             "the sample rate (fs) as per the Nyquist sampling theorem. Default: :attr:`fs/2`.",
    'f_min': "float.\n\tThe smallest frequency displayed. Also used for filters. Default: "
             ":attr:`df`.",
    'nperseg': "int.\n\tThe number of samples per data segment (for Welch's method). Default: "
               "``ceil(fs / df)`` or ``(npts + (nseg - 1) * noverlap) / nseg``.",
    'noverlap': "int.\n\tThe number of samples by which two adjacent segments overlap (for "
                "Welch's method). Default given by :attr:`DEFAULT_NOVERLAP_MAPPING`.",
    'n_pts': "int.\n\tThe total number of samples per data buffer retrieved from a call to "
             "``acquire``. Computed by default from :attr:`nperseg` and :attr:`noverlap`.",
    'n_seg': "int.\n\tThe number of segments to average over (to be used with Welch's method). "
             "Default: :attr:`DEFAULT_N_SEG`.",
    'n_avg': "int.\n\tThe number of outer repetitions of data buffer acquisition. Data will be "
             "averaged over all repetitions. Default: :attr:`DEFAULT_N_AVG`.",
}


def _validate_domain(f):
    """Decorates a bounds function to also validate allowed set of values."""
    @wraps(f)
    def wrapper(self, value):
        if f.__name__.startswith('_validate_'):
            # Python 3.9:
            # param = f.__name__.removeprefix('_validate_')
            param = f.__name__[10:]
        else:
            raise RuntimeError('Decorator only supports _validate_*() functions.')
        domain = getattr(self, f'_domain_{param}')
        if value not in domain:
            raise ValueError(f'{param} must be in {domain}, not {value}.')
        f(self, value)

    return wrapper


class interdependent_daq_property(property):  # noqa
    """A property that modifies the getter and automatically generates
    the setter such that compatibility with other properties and
    constraints is checked at get-/set-time and values are coerced into
    the annotated return type."""

    def __init__(self, fget: Callable[[Any], Any] | None = ...):
        def _id(x: _T) -> _T:
            return x

        def _fget(obj: DAQSettings) -> Any:
            to_allowed = getattr(obj, f'_to_allowed_{fget.__name__}', _id)
            return cast_fun(to_allowed(fget(obj)))

        def _fset(obj: DAQSettings, value: Any):
            old = obj.get(fget.__name__)
            to_allowed = getattr(obj, f'_to_allowed_{fget.__name__}', _id)
            make_compatible = getattr(obj, f'_make_compatible_{fget.__name__}',
                                      lambda value: obj.__setitem__(fget.__name__, value))

            # First set the value given without checking it, then pass to make_compatible to issue
            # warnings if it needed to be adjusted
            obj[fget.__name__] = value
            make_compatible(cast_fun(to_allowed(value)))
            try:
                getattr(obj, f'_validate_{fget.__name__}', _id)(obj[fget.__name__])
            except ValueError:
                if old is not None:
                    obj[fget.__name__] = old
                else:
                    obj.pop(fget.__name__)
                raise

        try:
            if version.parse(platform.python_version()) < version.parse('3.10'):
                # inspect.get_annotations not available, hack it
                return_type = getattr(fget, '__annotations__', {})['return']
            else:
                return_type = inspect.get_annotations(fget)['return']
            if isinstance(return_type, str):
                cast_fun = getattr(builtins, return_type)
            elif isinstance(return_type, type):
                cast_fun = return_type
            else:
                raise TypeError
        except KeyError:
            cast_fun = _id
        except (TypeError, AttributeError):
            raise RuntimeError(f'Return type annotation {return_type} not a builtin type; not '
                               'supported.')

        __type__, __doc__ = _doc_.get(fget.__name__).split('.\n\t')
        _fget.__doc__ = __doc__
        _fget.__annotations__['return'] = __type__
        super().__init__(_fget, _fset)


class DAQSettings(dict):
    """A dictionary with interdependent properties.

    Parameters that can depend on the value of other parameter have
    getters and setters that are aware of those interdependencies.
    Thus, for these parameters, this should be the preferred method of
    getting and setting over dictionary-style getitem and setitem.

    To convert to a keyword-argument dictionary, use
    :meth:`to_consistent_dict`.

    The class can be used just like a regular dictionary. However,
    there are the following special, interdependent parameters that
    will be parsed for consistency upon calling
    :meth:`to_consistent_dict` or setting the attribute.

    Parameters
    ----------
    """
    __doc__ = (
        __doc__.replace(4*' ', '')
        + '\n'.join((f'{key} : {val}' for key, val in _doc_.items()))
        + textwrap.dedent(
            """
            Examples
            --------
            There are default settings for each parameter:

            >>> DAQSettings()
            {}
            >>> DAQSettings().to_consistent_dict()  #doctest: +NORMALIZE_WHITESPACE
            {'fs': 10000.0,
             'df': 1.0,
             'f_max': 5000.0,
             'f_min': 1.0,
             'nperseg': 10000,
             'noverlap': 5000,
             'n_seg': 5,
             'n_pts': 30000,
             'n_avg': 1}

            User-settings can be passed when instantiating, and the remaining
            dependent parameters are automatically derived:

            >>> s = DAQSettings(fs=1234, n_seg=10)
            >>> s
            {'fs': 1234, 'n_seg': 10}
            >>> s.to_consistent_dict()  #doctest: +NORMALIZE_WHITESPACE
            {'fs': 1234.0,
             'n_seg': 10,
             'df': 1.0,
             'f_max': 617.0,
             'f_min': 1.0,
             'nperseg': 1234,
             'noverlap': 617,
             'n_pts': 6787,
             'n_avg': 1}

            Parameters have getters and setters. When getting, a value
            consistent with others is returned, when setting, the consistency is
            checked:

            >>> s.f_min
            1.0
            >>> s.f_min = 3
            >>> s.f_min
            3.0
            >>> s.f_max = 1000  #doctest: +NORMALIZE_WHITESPACE
            Traceback (most recent call last):
                ...
            ValueError: f_max must be in ContinuousInterval(lower=3.0,
            upper=617.0), not 1000.0.

            Consistency is not checked at instantiation time, only when using
            setters or converting to a plain consistent dictionary:

            >>> s = DAQSettings(fs=1e3, f_max=1e3)  # works
            >>> s.to_consistent_dict()  #doctest: +NORMALIZE_WHITESPACE
            Traceback (most recent call last):
                ...
            python_spectrometer.daq.settings.ResolutionError:
            Settings are inconsistent or not compatible with constraints.
            Parsed so far: {'fs': 1000.0, 'f_max': 1000.0, 'df': 1.0, 'nperseg': 1000}

            """
        )
    )

    # Rounding precision for comparing floating point values
    PRECISION: int = 10

    # The following attributes can be overridden by subclasses to implement
    # hardware constraints.
    # There are defaults only for a subset of parameters so that solving for consistency is not
    # impossible.
    DEFAULT_FS: float = 10e3
    DEFAULT_DF: float = 1.0
    DEFAULT_N_SEG: int = 5
    DEFAULT_N_AVG: int = 1
    # The default mapping to obtain noverlap from nperseg given as the
    # two-tuple (a, b) that fulfills nperseg = noverlap // a + b
    DEFAULT_NOVERLAP_MAPPING: tuple[int, int] = (2, 0)

    # Override these to constrain parameters to certain sets allowed by hardware. An empty set
    # means no restrictions.
    ALLOWED_FS: _FloatDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_DF: _FloatDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_F_MAX: _FloatDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_F_MIN: _FloatDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_NOVERLAP: _IntDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_N_PTS: _IntDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_N_SEG: _IntDomainT = BoundedSet(precision=PRECISION)
    ALLOWED_N_AVG: _IntDomainT = BoundedSet(precision=PRECISION)

    @property
    def ALLOWED_NPERSEG(self) -> _IntDomainT:
        return self.ALLOWED_N_PTS

    def _lower_bound_fs(self) -> float:
        return self._domain_f_max.min() * 2

    def _upper_bound_fs(self) -> float:
        return inf

    def _lower_bound_df(self) -> float:
        return finfo(float).eps

    def _upper_bound_df(self) -> float:
        return self._domain_f_min.max()

    def _lower_bound_f_max(self) -> float:
        return self.get('f_min') or self._infer_f_min() or finfo(float).eps

    def _upper_bound_f_max(self) -> float:
        fs = self.get('fs', self._infer_fs())
        return fs / 2 if fs is not None else inf

    def _lower_bound_f_min(self) -> float:
        df = self.get('df', self._infer_df())
        return df if df is not None else finfo(float).eps

    def _upper_bound_f_min(self) -> float:
        return self.get('f_max') or self._infer_f_max() or inf

    def _lower_bound_nperseg(self) -> int:
        return self.get('noverlap', 0) + 1

    def _upper_bound_nperseg(self) -> int | float:
        return self.get('n_pts') or self._domain_n_pts.max()

    def _lower_bound_noverlap(self) -> int | float:
        ub_nperseg = self._domain_nperseg.max()
        nperseg = self.get('nperseg') or self._infer_nperseg() or ub_nperseg
        bound = 0
        if 'n_seg' in self and self['n_seg'] > 2:
            return max(bound, nperseg - (ub_nperseg - nperseg) / (self['n_seg'] - 2))
        return bound

    def _upper_bound_noverlap(self) -> int | float:
        ub_nperseg = self._domain_nperseg.max()
        nperseg = self.get('nperseg') or self._infer_nperseg() or ub_nperseg
        bound = nperseg - 1
        if not isinf(ub_nperseg) and 'n_seg' in self:
            return min(bound, nperseg - (ub_nperseg - nperseg) // self['n_seg'])
        return bound

    def _lower_bound_n_pts(self) -> int:
        a, b = self.DEFAULT_NOVERLAP_MAPPING
        n_seg = self.get('n_seg') or self._infer_n_seg() or 1
        nperseg = self.get('nperseg') or self._infer_nperseg() or self._domain_nperseg.min()
        noverlap = self.get('noverlap') or self._infer_noverlap() or nperseg // a + b
        return int(nperseg + (n_seg - 1) * (nperseg - noverlap))

    def _upper_bound_n_pts(self) -> int | float:
        return inf

    def _lower_bound_n_seg(self) -> int | float:
        return 1

    def _upper_bound_n_seg(self) -> int | float:
        return inf

    def _lower_bound_n_avg(self) -> int | float:
        return 1

    def _upper_bound_n_avg(self) -> int | float:
        return inf

    # The _domain_* properties cannot be cached because in principle both ALLOWED_* and Interval
    # can be dynamic.
    @property
    def _domain_fs(self) -> _FloatDomainT:
        return self.ALLOWED_FS & ContinuousInterval(self._lower_bound_fs, self._upper_bound_fs,
                                                    self.PRECISION)

    @property
    def _domain_df(self) -> _FloatDomainT:
        return self.ALLOWED_DF & ContinuousInterval(self._lower_bound_df, self._upper_bound_df,
                                                    self.PRECISION)

    @property
    def _domain_f_max(self) -> _FloatDomainT:
        return self.ALLOWED_F_MAX & ContinuousInterval(self._lower_bound_f_max,
                                                       self._upper_bound_f_max,
                                                       self.PRECISION)

    @property
    def _domain_f_min(self) -> _FloatDomainT:
        return self.ALLOWED_F_MIN & ContinuousInterval(self._lower_bound_f_min,
                                                       self._upper_bound_f_min,
                                                       self.PRECISION)

    @property
    def _domain_nperseg(self) -> _IntDomainT:
        return self.ALLOWED_NPERSEG & DiscreteInterval(self._lower_bound_nperseg,
                                                       self._upper_bound_nperseg,
                                                       self.PRECISION)

    @property
    def _domain_noverlap(self) -> _IntDomainT:
        return self.ALLOWED_NOVERLAP & DiscreteInterval(self._lower_bound_noverlap,
                                                        self._upper_bound_noverlap,
                                                        self.PRECISION)

    @property
    def _domain_n_pts(self) -> _IntDomainT:
        return self.ALLOWED_N_PTS & DiscreteInterval(self._lower_bound_n_pts,
                                                     self._upper_bound_n_pts,
                                                     self.PRECISION)

    @property
    def _domain_n_seg(self) -> _IntDomainT:
        return self.ALLOWED_N_SEG & DiscreteInterval(self._lower_bound_n_seg,
                                                     self._upper_bound_n_seg,
                                                     self.PRECISION)

    @property
    def _domain_n_avg(self) -> _IntDomainT:
        return self.ALLOWED_N_AVG & DiscreteInterval(self._lower_bound_n_avg,
                                                     self._upper_bound_n_avg,
                                                     self.PRECISION)

    @_validate_domain
    def _validate_fs(self, fs):
        if (inferred := self._infer_fs()) is not None and not self._isclose(inferred, fs):
            raise ValueError(f'fs not compatible with df and nperseg. actual = {fs}, inferred = '
                             f'{inferred}')

    @_validate_domain
    def _validate_df(self, df):
        if (inferred := self._infer_df()) is not None and not self._isclose(inferred, df):
            raise ValueError(f'df not compatible with fs and nperseg. actual = {df}, inferred = '
                             f'{inferred}')

    @_validate_domain
    def _validate_f_max(self, f_max):
        ...

    @_validate_domain
    def _validate_f_min(self, f_min):
        ...

    @_validate_domain
    def _validate_nperseg(self, nperseg):
        if (inferred := self._infer_nperseg()) is not None and nperseg != inferred:
            raise ValueError(f'nperseg is incompatible. actual = {nperseg}, inferred = {inferred}')

    @_validate_domain
    def _validate_noverlap(self, noverlap):
        ...

    @_validate_domain
    def _validate_n_pts(self, n_pts):
        ...

    @_validate_domain
    def _validate_n_seg(self, n_seg):
        if (inferred := self._infer_n_seg()) is not None and n_seg != inferred:
            raise ValueError('n_seg not compatible with nperseg, n_pts, and noverlap. actual = '
                             f'{n_seg}, inferred = {inferred}')

    @_validate_domain
    def _validate_n_avg(self, n_avg):
        ...

    def _to_allowed_fs(self, fs: float | None) -> float | None:
        if fs is None:
            return None

        fs_prev = fs
        if not isinf(df := self.get('df', self.get('f_min', inf))):
            # Constraints on nperseg constrain fs
            fs = df * self._domain_nperseg.next_largest(fs / df)
        if not self._isclose(fs, fs_prev):
            # Chicken-egg problem here with nperseg and df, so cannot use setter
            self['nperseg'] = self._domain_nperseg.next_largest(fs_prev / df)
            self._make_compatible_df(fs_prev / self['nperseg'])
            return self._to_allowed_fs(fs_prev)
        if 'nperseg' in self:
            # Constraints on df constrain fs
            fs = self._domain_df.next_smallest(fs / self['nperseg']) * self['nperseg']
        if not self._isclose(fs, fs_prev):
            self['df'] = self._domain_df.next_closest(fs_prev / self['nperseg'])
            self._make_compatible_nperseg(ceil(self._domain_df.round(fs_prev / self['df'])))
            return self._to_allowed_fs(fs_prev)
        # Constraints on fs itself
        if not isinf(df) and not self._domain_fs.round(fs / df) % 1:
            # fs might be due to ceil-ing when inferring nperseg. Use next_closest
            fs = self._domain_fs.next_closest(fs)
        else:
            fs = self._domain_fs.next_largest(fs)
        if not self._isclose(fs, fs_prev):
            self._make_compatible_fs(fs)
            return fs
        # Finally, as a last resort test if the parameters match. If not, try to adjust nperseg
        if not isinf(df) and 'nperseg' in self:
            fs = df / self['nperseg']
        if not self._isclose(fs, fs_prev):
            self['fs'] = self._domain_fs.next_closest(fs_prev)
            self._make_compatible_nperseg(
                self._domain_nperseg.next_closest(self['fs'] / df)
            )
            return self['fs']

        return fs

    def _to_allowed_df(self, df: float | None) -> float | None:
        if df is None:
            return None

        df_prev = df
        if 'nperseg' in self:
            # Constraints on fs constrain df
            df = self._domain_fs.next_largest(df * self['nperseg']) / self['nperseg']
        if not self._isclose(df, df_prev):
            self['fs'] = self._domain_fs.next_closest(df_prev * self['nperseg'])
            # Use df instead of df_prev here because we preferentially adjust df over fs or nperseg
            self._make_compatible_nperseg(ceil(self._domain_fs.round(self['fs'] / df)))
            return self._to_allowed_df(df)
        if not isinf(fs := self.get('fs', self.get('f_max', inf) * 2)):
            # Constraints on nperseg constrain df
            df = fs / self._domain_nperseg.next_largest(fs / df)
        if not self._isclose(df, df_prev):
            self['nperseg'] = self._domain_nperseg.next_largest(fs / df_prev)
            self._make_compatible_fs(df * self['nperseg'])
            return self._to_allowed_df(df)
        # Constraints on df itself
        df = self._domain_df.next_smallest(df)
        if not self._isclose(df, df_prev):
            self._make_compatible_df(df)
            return df
        # Finally, as a last resort test if the parameters match. If not, try to adjust nperseg
        if not isinf(fs) and 'nperseg' in self:
            df = fs / self['nperseg']
        if not self._isclose(df, df_prev):
            self['df'] = self._domain_df.next_closest(df_prev)
            self._make_compatible_nperseg(
                self._domain_nperseg.next_closest(fs / self['df'])
            )
            return self['df']

        return df

    def _to_allowed_nperseg(self, nperseg: int | None) -> int | None:
        # account for rounding when either fs or df have been set to a weird float and the other
        # defaults to an integer as well as hardware constraints.
        # As typical hardware will more likely have constraints on sample rate, choose altering df
        # preferentially
        if nperseg is None:
            return None

        # Unlike for fs and df, nperseg is always rounded up, so the flow here is a bit different
        # to those as there is almost always the need to adjust fs or df, even if they are not
        # constrained.
        nperseg_prev = nperseg
        fs = self.get('fs', self.get('f_max', inf) * 2)
        df = self.get('df', self.get('f_min', inf))
        if not isinf(df):
            # Constraints on fs constrain nperseg through df/f_min
            nperseg = ceil(self._domain_df.round(self._domain_fs.next_largest(df * nperseg) / df))
        if nperseg != nperseg_prev:
            self['fs'] = self._domain_fs.next_largest(fs if not isinf(fs) else df * nperseg_prev)
            self._make_compatible_df(self['fs'] / nperseg_prev)
            return self._to_allowed_nperseg(nperseg_prev)
        if not isinf(fs):
            # Constraints on df constrain nperseg through fs/f_max
            nperseg = ceil(self._domain_fs.round(fs / self._domain_df.next_smallest(fs / nperseg)))
        if nperseg != nperseg_prev:
            self['df'] = self._domain_df.next_closest(df if not isinf(df) else fs * nperseg_prev)
            self._make_compatible_fs(self['df'] * nperseg_prev)
            return self._to_allowed_nperseg(nperseg_prev)
        # Constraints on nperseg itself
        nperseg = self._domain_nperseg.next_largest(nperseg)
        if nperseg != nperseg_prev:
            self._make_compatible_nperseg(nperseg)
            return nperseg
        # Finally, as a last resort test if the parameters match. If not, try to adjust df
        if not isinf(df) and not isinf(fs):
            nperseg = ceil(self._domain_fs.round(fs / df))
        if nperseg != nperseg_prev:
            self['nperseg'] = self._domain_nperseg.next_closest(nperseg_prev)
            self._make_compatible_df(self._domain_df.next_closest(self['fs'] / self['nperseg']))
            return self['nperseg']

        return nperseg

    def _make_compatible_fs(self, fs: float):
        if 'fs' in self and not self._isclose(fs, self['fs']):
            warnings.warn(f"Need to change fs from {self['fs']} to {fs}. This is most "
                          "likely due to rounding or hardware constraints.",
                          UserWarning, stacklevel=2)
            self.fs = fs
        if 'f_max' in self:
            if self['f_max'] * 2 > self.get('fs', fs):
                warnings.warn(f"Need to change f_max from {self['f_max']} to {fs / 2}. This is "
                              "most likely due to rounding or hardware constraints.",
                              UserWarning, stacklevel=2)
                self.f_max = fs / 2
            if 'fs' not in self:
                # Need to set fs so that ceil(fs/df) is integral
                self.fs = fs

    def _make_compatible_df(self, df: float):
        if 'df' in self and not self._isclose(df, self['df']):
            warnings.warn(f"Need to change df from {self['df']} to {df}. This is most "
                          "likely due to rounding or hardware constraints.",
                          UserWarning, stacklevel=2)
            self.df = df
        if 'f_min' in self:
            if self['f_min'] < self.get('df', df):
                warnings.warn(f"Need to change f_min from {self['f_min']} to {df}. This is "
                              "most likely due to rounding or hardware constraints.",
                              UserWarning, stacklevel=2)
                self.f_min = df
            if 'df' not in self:
                # Need to set df so that ceil(fs/df) is integral
                self.df = df

    def _make_compatible_nperseg(self, nperseg: int):
        if 'nperseg' not in self:
            self['nperseg'] = nperseg
        if nperseg != self['nperseg']:
            warnings.warn(f"Need to change nperseg from {self['nperseg']} to {nperseg}. This "
                          "is most likely due to rounding or hardware constraints.",
                          UserWarning, stacklevel=2)
            self.nperseg = nperseg
        if self.get('n_pts', inf) < self['nperseg']:
            warnings.warn(f"Need to change n_pts from {self['n_pts']} to {self['nperseg']}"
                          ". This is most likely due to rounding or hardware constraints.",
                          UserWarning, stacklevel=2)
            self.n_pts = nperseg
            if self.get('n_seg', 0) > 1:
                warnings.warn(f"Need to change n_seg from {self['n_seg']} to 1. This is "
                              "most likely due to rounding or hardware constraints.",
                              UserWarning, stacklevel=2)

    def _infer_fs(self, default: bool = False) -> float | None:
        nperseg = self.get('nperseg') or self._infer_nperseg(default)
        if nperseg is not None:
            if 'df' in self:
                return self['df'] * nperseg
            if 'f_min' in self:
                return self['f_min'] * nperseg
        if default:
            if 'f_max' in self:
                return self['f_max'] * 2
            return self.DEFAULT_FS
        return None

    def _infer_df(self, default: bool = False) -> float | None:
        nperseg = self.get('nperseg') or self._infer_nperseg(default)
        if nperseg is not None:
            if 'fs' in self:
                return self['fs'] / nperseg
            if 'f_max' in self:
                return self['f_max'] * 2 / nperseg
        if default:
            if 'f_min' in self:
                return self['f_min']
            return self.DEFAULT_DF
        return None

    def _infer_f_max(self, default: bool = False) -> float | None:
        if (fs := (self.get('fs') or self._infer_fs(default))) is not None:
            return fs / 2
        return None

    def _infer_f_min(self, default: bool = False) -> float | None:
        if (df := (self.get('df') or self._infer_df(default))) is not None:
            return df
        return None

    def _infer_nperseg(self, default: bool = False) -> int | None:
        # user-set fs or df take precedence over noverlap
        if 'fs' in self and 'df' in self:
            return ceil(self._domain_fs.round(self['fs'] / self['df']))
        if 'n_pts' in self:
            if 'noverlap' in self and 'n_seg' in self:
                return int((self['n_pts'] + (self['n_seg'] - 1) * self['noverlap'])
                           / self['n_seg'])
            if default:
                n_seg = self.get('n_seg', self.DEFAULT_N_SEG)
                if 'noverlap' not in self:
                    a, b = self.DEFAULT_NOVERLAP_MAPPING
                    return ceil((self['n_pts'] + (n_seg - 1) * b) / (n_seg - (n_seg - 1) / a))
                return int((self['n_pts'] + (n_seg - 1) * self['noverlap']) / n_seg)

        # Could not infer from directly related quantities. Try with f_min/f_max and their defaults
        df = self.get('df', self.get('f_min', self.DEFAULT_DF if default else inf))
        fs = self.get('fs', self.get('f_max', self.DEFAULT_FS / 2 if default else inf) * 2)
        if not isinf(df) and not isinf(fs):
            # In principle this should be self._domain_nperseg.next_largest(), but that recurses
            # infinitely. So we do what we can.
            return min(ceil(self._domain_fs.round(fs / df)), self._upper_bound_nperseg())
        return None

    def _infer_noverlap(self, default: bool = False) -> int | None:
        if self.get('n_seg') == 1:
            # arbitrary
            return 0
        nperseg = self.get('nperseg', self._infer_nperseg())
        n_pts = self.get('n_pts') or self._infer_n_pts() or self._domain_n_pts.max()
        if nperseg is not None:
            if not isinf(n_pts) and 'n_seg' in self:
                return min(ceil(nperseg - (n_pts - nperseg) / (self['n_seg'] - 1)),
                           self._domain_noverlap.max())
            if default:
                a, b = self.DEFAULT_NOVERLAP_MAPPING
                return nperseg // a + b
        return None

    def _infer_n_seg(self, default: bool = False) -> int | None:
        nperseg = self.get('nperseg') or self._infer_nperseg()
        n_pts = self.get('n_pts') or self._infer_n_pts() or self._domain_n_pts.max()
        noverlap = self.get('noverlap') or self._infer_noverlap()
        if default and nperseg is not None and not isinf(n_pts):
            a, b = self.DEFAULT_NOVERLAP_MAPPING
            noverlap = noverlap or nperseg // a + b
        if nperseg is not None and not isinf(n_pts) and noverlap is not None:
            return floor((n_pts - noverlap) / (nperseg - noverlap))
        if default:
            return self.DEFAULT_N_SEG
        return None

    def _infer_n_pts(self) -> int | None:
        nperseg = self.get('nperseg') or self._infer_nperseg()
        if nperseg is not None and 'n_seg' in self and 'noverlap' in self:
            return int(nperseg + (self['n_seg'] - 1) * (nperseg - self['noverlap']))
        return None

    def _isclose(self, a, b) -> bool:
        return abs(a - b) < 1 / 10**self.PRECISION

    def setdefault(self, key: _KT, default: _VT = ...) -> _VT:
        # Override the dict method to use property setters if available.
        if key in self.interdependent_settings:
            if key not in self:
                setattr(self, key, default)
            return self.get(key)
        return super().setdefault(key, default)

    def to_consistent_dict(self) -> dict[str, _RealT]:
        """Return a regular dictionary with entries checked for
        consistency."""
        # All settings that are not (yet) dict entries at this point are to be inferred
        inferred_settings = {name: obj for name, obj in self.interdependent_settings.items()
                             if name not in self}
        # Make sure we parse settings that were set by the user first
        all_settings = {**self, **vars(self), **inferred_settings}

        # The interdependent settings have two branches that connect to the central quantity
        # nperseg
        #  - The first are the frequencies fs, df, f_max, f_min
        #  - The second are the enumerators n_seg, noverlap, n_pts
        # By defining the order in which we parse the settings we make sure there are no
        # inconsistencies
        ordered_settings = ['nperseg', 'fs', 'df', 'f_max', 'f_min', 'n_seg', 'noverlap', 'n_pts']
        ordered_settings.extend([setting for setting in all_settings
                                 if setting not in ordered_settings])

        # Work on a copy which we can modify at will
        copied = copy(self)
        for setting in ordered_settings:
            try:
                all_settings[setting] = getattr(copied, setting)
                getattr(copied, f'_validate_{setting}')(all_settings[setting])
            except AttributeError:
                pass
            except ValueError as err:
                raise ResolutionError('Settings are inconsistent or not compatible with '
                                      f'constraints. Parsed so far: {copied}') from err
            # bookkeeping so that the object we use to check for consistency has all the facts
            copied[setting] = all_settings[setting]
        return all_settings

    @property
    def interdependent_settings(self) -> dict[str, interdependent_daq_property]:
        """All instances of :class:`interdependent_daq_property`."""
        return {name: obj for name, obj
                # Iterate over all classes in the mro (except dict and object) to include possible
                # child classes.
                in ChainMap(*(vars(cls) for cls in type(self).__mro__[:-2])).items()
                if isinstance(obj, interdependent_daq_property)}

    @interdependent_daq_property
    def fs(self) -> float:
        if 'fs' in self:
            return self['fs']
        if (nperseg := (self.get('nperseg') or self._infer_nperseg())) is not None:
            df = self.setdefault('df', self._infer_df(default=True))
            return df * nperseg
        return self.setdefault('fs', self._infer_fs(default=True))

    @interdependent_daq_property
    def df(self) -> float:
        if 'df' in self:
            return self['df']
        if (nperseg := (self.get('nperseg') or self._infer_nperseg())) is not None:
            fs = self.setdefault('fs', self._infer_fs(default=True))
            return fs / nperseg
        return self.setdefault('df', self._infer_df(default=True))

    @interdependent_daq_property
    def f_max(self) -> float:
        if 'f_max' in self:
            return self['f_max']
        return self.fs / 2

    @interdependent_daq_property
    def f_min(self) -> float:
        if 'f_min' in self:
            return self['f_min']
        return self.df

    @interdependent_daq_property
    def nperseg(self) -> int:
        if 'nperseg' in self:
            return self['nperseg']
        if (nperseg := self._infer_nperseg()) is not None:
            return nperseg
        return self.setdefault('nperseg', ceil(self._domain_fs.round(self.fs / self.df)))

    @interdependent_daq_property
    def noverlap(self) -> int:
        if 'noverlap' in self:
            return self['noverlap']
        if (noverlap := self._infer_noverlap()) is not None:
            return noverlap
        a, b = self.DEFAULT_NOVERLAP_MAPPING
        return self.setdefault('noverlap', self.nperseg // a + b)

    @interdependent_daq_property
    def n_seg(self) -> int:
        if 'n_seg' in self:
            return self['n_seg']
        return self.setdefault('n_seg', self._infer_n_seg(default=True))

    @interdependent_daq_property
    def n_pts(self) -> int:
        if 'n_pts' in self:
            return self['n_pts']
        if (n_pts := self._infer_n_pts()) is not None:
            return n_pts
        return self.setdefault('n_pts',
                               self.nperseg + (self.n_seg - 1) * (self.nperseg - self.noverlap))

    @interdependent_daq_property
    def n_avg(self) -> int:
        return self.setdefault('n_avg', self.DEFAULT_N_AVG)


class ResolutionError(Exception):
    """Indicates DAQSettings cannot be resolved to a consistent dict."""
