import copy
import inspect
import os
import platform
import shelve
import sys
import warnings
from collections.abc import Generator, Iterator, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from pprint import pprint
from queue import Empty, LifoQueue, Queue
from threading import Event, Thread
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, cast
from unittest import mock

import dill
import numpy as np
from matplotlib import colors
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from qutil import io, misc
from qutil.functools import cached_property, chain, partial
from qutil.io import AsyncDatasaver
from qutil.itertools import count
from qutil.plotting import is_using_mpl_gui_backend, live_view
from qutil.signal_processing.real_space import Id, welch
from qutil.typecheck import check_literals
from qutil.ui import progressbar

from ._audio_manager import WaveformPlaybackManager
from ._plot_manager import PlotManager, _asinh_scale_maybe
from .daq import settings as daq_settings
from .daq.base import DAQ

_keyT = Union[int, str, tuple[int, str]]
_pathT = Union[str, os.PathLike]
_styleT = Union[str, os.PathLike, dict]
_styleT = Union[None, _styleT, list[_styleT]]


def _forward_property(cls: type, member: str, attr: str):
    def getter(self):
        return getattr(getattr(self, member), attr)

    def setter(self, val):
        return setattr(getattr(self, member), attr, val)

    return property(getter, setter, doc=getattr(cls, attr).__doc__)


class _Unpickler(dill.Unpickler):
    PATHTYPE = type(Path())

    def find_class(self, module, name):
        if module.startswith("pathlib") and name.endswith("Path"):
            return self.PATHTYPE
        return super().find_class(module, name)


class FrequencyLiveView(live_view.IncrementalLiveView2D):
    """Spectrum live view. See :meth:`.Spectrometer.live_view`."""

    def _add_axes(self, ax: Optional[Axes] = None):
        super()._add_axes(ax)
        self.axes['line'].grid()


class TimeLiveView(live_view.BatchedLiveView1D):
    """Timetrace live view. See :meth:`.Spectrometer.live_view`."""

    def _add_axes(self, ax: Optional[Axes] = None):
        super()._add_axes(ax)
        self.axes['main'].grid()


class Spectrometer:
    r"""A spectrometer to acquire and display power spectral densities.

    Spectra are acquired using :meth:`take` and identified by an
    index-comment two-tuple. The data is measured and processed by
    either a user-supplied function or
    :func:`~qutil:qutil.signal_processing.real_space.welch`.

    Parameters
    ----------
    daq : DAQ
        A :class:`.daq.core.DAQ` object handling data acquisition. This
        class abstracts away specifics of how to interact with the
        hardware to implement an interface that is independent of the
        lower-level driver. See the :class:`.DAQ` docstring for more
        information.

        If not given, the instance is read-only and can only be used
        for processing and plotting old data.
    psd_estimator : Callable or kwarg dict
        If callable, a function with signature::

            f(data, **settings) -> (ndarray, ndarray, ndarray)

        that takes the data acquired by the DAQ and the settings
        dictionary and estimates the PSD, returning a tuple of
        (PSD, frequencies, iFFTd data). If dict, a keyword-argument
        dictionary to be passed to
        :func:`~qutil:qutil.signal_processing.real_space.welch` as a PSD
        estimator.

        .. note::

            If a dict, the keyword 'density' will be excluded when
            called since it is always assumed that the ``psd_estimator``
            will return a power spectral density.

    procfn : Callable or sequence of Callable
        A (sequence of) callable with signature::

            f(timetrace, **settings) -> ndarray

        that performs processing steps on the raw timeseries data.
        The function is called with the settings as returned by
        :meth:`.DAQ.setup`. If a sequence, the functions are applied
        from left-to-right, e.g., if ``procfn = [a, b, c]``, then
        it is applied as ``c(b(a(xf, f, **s), f, **s), f, **s)``.
    plot_raw : bool, default False
        Plot the raw spectral data on a secondary y-axis using a
        smaller alpha (more transparent line). Can also be toggled
        dynamically by setting :attr:`plot_raw`.
    plot_timetrace : bool, default False
        Plot the most recent raw timeseries data on a new subplot.
        Can also be toggled dynamically by setting
        :attr:`plot_timetrace`.
    plot_cumulative : bool, default False
        Plot the cumulative data given by

        .. math::
            \mathrm{RMS}_S(f)^2 = \int_{f_\mathrm{min}}^f\mathrm{d}
                f^\prime\,S(f^\prime)

        with :math:`\mathrm{RMS}_S(f)` the root-mean-square of the PSD
        :math:`S(f^\prime)` up to frequency :math:`f^\prime` on a new
        subplot. If :attr:`plot_density` is False, the spectrum instead
        of the PSD is used, but note that this does not make a lot of
        sense.

        If :attr:`plot_dB_scale` is True, the log-ratio of
        :math:`\mathrm{RMS}_S(f)` with that of the reference data is
        plotted.

        Can also be toggled dynamically by setting
        :attr:`plot_cumulative`.
    plot_negative_frequencies : bool, default True
        Plot negative frequencies for two-sided spectra (in case the
        time-series data is complex). For ``matplotlib >= 3.6`` an
        ``asinh``, otherwise a linear scale is used. Can also be
        toggled dynamically by setting
        :attr:`plot_negative_frequencies`.
    plot_absolute_frequencies : bool, default True
        For lock-in measurements: plot the physical frequencies at the
        input of the device, not the downconverted ones. This means the
        displayed frequencies are shifted by the demodulation
        frequency, which must be present in the settings under the
        keyword 'freq'. Can also be toggled dynamically by setting
        :attr:`plot_absolute_frequencies`.
    plot_amplitude : bool, default True
        Plot the amplitude spectral density / spectrum (the square root)
        instead of the power. Also applies to the cumulative plot
        (:attr:`plot_cumulative`), in which case that plot
        corresponds to the cumulative mean square instead of the
        root-mean-square (RMS) if plotting the density. Can also be
        toggled dynamically by setting :attr:`plot_amplitude`.

        .. note::
            :attr:`psd_estimator` should always return a power spectral
            density, the conversions concerning this parameter are done
            only when plotting.

    plot_density : bool, default True
        Plot the * spectral density rather than the * spectrum. If
        False and plot_amplitude is True, i.e. if the amplitude spectrum
        is plotted, the height of a peak will give an estimate of the
        RMS amplitude. Can also be toggled dynamically by setting
        :attr:`plot_density`.

        .. note::
            :attr:`psd_estimator` should always return a power spectral
            density, the conversions concerning this parameter are done
            only when plotting.

    plot_cumulative_normalized : bool, default False
        Normalize the cumulative data so that it corresponds to the CDF.
        Can also be toggled dynamically by setting
        :attr:`plot_cumulative_normalized`.
    plot_style : str, Path, dict, list thereof, or None, default 'fast'
        Use a matplotlib style sheet for plotting. All styles available
        are given by :func:`matplotlib:matplotlib.style.available`. Set
        to None to disable styling and use default parameters. Note that
        line styles in ``prop_cycle`` override style settings.
    plot_update_mode : {'fast', 'always', 'never'}
        Determines how often the event queue of the plot is flushed.

         - 'fast' : queue is only flushed after all plot calls are
           done. Lines might not show upon every average update. By
           experience, whether lines are updated inside a loop depends
           on the DAQ backend. (default)
         - 'always' : forces a flush before and after plot calls are
           done, but slows down the entire plotting by a factor of
           order unity.
         - 'never' : Queue is never flushed explicitly. Might yield
           slightly better performance when threaded acquisition is
           enabled.
    plot_dB_scale : bool, default False
        Plot data in dB relative to a reference spectrum instead of
        in absolute units. The reference spectrum defaults to the first
        acquired, but can be set using :meth:`set_reference_spectrum`.
    threaded_acquisition : bool, default True
        Acquire data in a separate thread. This keeps the plot window
        responsive while acquisition is running.
    blocking_acquisition : bool, default False
        Block the interpreter while acquisition is running. This might
        prevent concurrency errors when running a measurement script
        that performs multiple acquisitions or plot actions.
    prop_cycle : cycler.Cycler
        A property cycler for styling the plotted lines.
    play_sound : bool, default False
        Play the recorded noise sample out loud.
    audio_amplitude_normalization : Union[Literal["single_max"], float], default "single_max"
        The factor with with which the waveform is divided by to
        normalize the waveform. This can be used to set the volume.
        The default "single_max" normalized each sample depending on
        only that one sample, thus the volume might not carry significant
        information. Alternatively a factor like 1e-9 can be given to
        specify that 1nA of signal corresponds to the full audio output
        amplitude.
    savepath : str or Path
        Directory where the data is saved. All relative paths, for
        example those given to :meth:`serialize_to_disk`, will be
        referenced to this.
    compress : bool
        Compress the data when saving to disk (using
        :func:`numpy:numpy.savez_compressed`).
    raw_unit : str
        The unit of the raw, unprocessed data returned by
        meth:`DAQ.acquire`.
    processed_unit : str
        The unit of the processed data. Can also be set dynamically by
        setting :attr:`processed_unit` in case it changed when using
        :meth:`reprocess_data`. Defaults to `raw_unit`.
    figure_kw, gridspec_kw, subplot_kw, legend_kw : Mappings
        Keyword arguments forwarded to the corresopnding matplotlib
        constructors.

    Examples
    --------
    Perform spectral estimation on simulated data using :mod:`qopt:qopt`
    as backend:

    >>> from pathlib import Path
    >>> from tempfile import mkdtemp
    >>> from python_spectrometer.daq import QoptColoredNoise
    >>> def spectrum(f, A=1e-4, exp=1.5, **_):
    ...     return A/f**exp
    >>> daq = QoptColoredNoise(spectrum)
    >>> spect = Spectrometer(daq, savepath=mkdtemp(), threaded_acquisition=False)
    >>> spect.take('a comment', f_max=2000, A=2e-4)
    >>> spect.print_keys()
     - (0, 'a comment')
    >>> spect.take('more comments', df=0.1, f_max=2000)
    >>> spect.print_keys()
     - (0, 'a comment')
     - (1, 'more comments')

    Hide and show functionality:

    >>> spect.hide(0)
    >>> spect.show('a comment')  # same as spect.show(0)
    >>> spect.drop(1)  # drops the spectrum from cache but leaves the data

    Save/recall functionality:

    >>> spect.serialize_to_disk('foo')
    >>> spect_loaded = Spectrometer.recall_from_disk(
    ...     spect.savepath / 'foo', daq
    ... )
    >>> spect_loaded.print_keys()
     - (0, 'a comment')
    >>> spect.print_settings('a comment')
    Settings for key (0, 'a comment'):
    {'A': 0.0002,
     'df': 1.0,
     'f_max': 2000.0,
     'f_min': 1.0,
     'fs': 4000.0,
     'n_avg': 1,
     'n_pts': 12000,
     'n_seg': 5,
     'noverlap': 2000,
     'nperseg': 4000}

    Use threaded acquisition to avoid blocking the interpreter and keep
    the figure responsive:

    >>> spect.threaded_acquisition = True
    >>> spect.take(n_avg=5, delay=True, progress=False)

    When the spectrometer is still acquiring, starting a new acquisition
    errors.

    >>> spect.take()
    Traceback (most recent call last):
        ...
    RuntimeError: Spectrometer is currently acquiring.

    To check the acquisition status, use either the :attr:`acquiring`
    attribute or block until ready (defeats the purpose though).

    >>> spect.block_until_ready()
    >>> spect.take(n_avg=5, delay=True, progress=False)
    >>> spect.acquiring
    True
    >>> spect.block_until_ready()
    >>> spect.acquiring
    False

    Use the audio interface to listen to the noise:

    >>> spect_with_audio = Spectrometer(daq, savepath=mkdtemp(), play_sound=True,
    ...                                 threaded_acquisition=False)
    >>> spect_with_audio.take('a comment', f_max=20000, A=2e-4)
    >>> spect_with_audio.audio_stream.stop()

    Instead of taking spectra one-by-one, it is also possible to
    continuously acquire data and live-plot the obtained power spectra,
    using :mod:`qutil:qutil.plotting.live_view` in the background. In
    this mode, data is not saved to disk, and it is in general less
    flexible (mostly because things aren't implement yet -- open a PR
    :) ).

    To start the live mode, call :meth:`live_view` with the settings
    for data acquisition just like :meth:`take`. The method returns the
    live view object and continues to run in the background.

    >>> speck = Spectrometer(daq, savepath=mkdtemp())
    >>> view, = speck.live_view(fs=1e4)

    We can use the view to control the state, like pausing or manually
    rescaling. See the qutil documentation for the
    :mod:`qutil:qutil.plotting.live_view` module for more information.

    If the :attr:`plot_timetrace` flag is set, another live view for the
    real-time data is instanatiated:

    >>> import matplotlib.pyplot as plt
    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()
    >>> speck.plot_timetrace = True
    >>> freq_view, time_view = speck.live_view()

    The data acquisition can be stopped either by calling
    :meth:`~qutil:qutil.plotting.live_view.LiveViewBase.stop` or simply
    by closing the figure.

    >>> plt.pause(1e-3)  # for doctest
    >>> freq_view.stop()

    Interrupting one live view will also kill the other.

    Live views can also be run in a separate process using
    :mod:`multiprocessing`. Simply pass ``in_process=True``. Note that
    it can take a while for the figure to show (especially on
    Windows):

    >>> import os, time
    >>> live_view_kw = {'backend': 'agg' if 'GITLAB_CI' in os.environ else None,
    ...                 'context_method': 'spawn'}
    >>> view_proxies = speck.live_view(in_process=True,
    ...                                live_view_kw=live_view_kw)
    >>> while not all(proxy.is_running() for proxy in view_proxies):
    ...     time.sleep(50e-3)

    Stop the views:

    >>> for proxy in view_proxies:
    ...     proxy.stop()
    ...     proxy.process.terminate()

    >>> plt.close('all')

    """
    _OLD_PARAMETER_NAMES = {
        'plot_cumulative_power': 'plot_cumulative',
        'plot_cumulative_spectrum': 'plot_cumulative',
        'cumulative_normalized': 'plot_cumulative_normalized',
        'amplitude_spectral_density': 'plot_amplitude'
    }
    # Expose plot properties from plot manager
    _to_expose = ('fig', 'ax', 'ax_raw', 'leg', 'plot_raw', 'plot_timetrace', 'plot_cumulative',
                  'plot_negative_frequencies', 'plot_absolute_frequencies', 'plot_amplitude',
                  'plot_density', 'plot_cumulative_normalized', 'plot_style', 'plot_dB_scale',
                  'prop_cycle', 'reference_spectrum', 'processed_unit')

    # type checkers
    fig: Figure
    ax: Sequence[Axes]
    ax_raw: Sequence[Axes]
    leg: Legend
    plot_raw: bool
    plot_timetrace: bool
    plot_cumulative: bool
    plot_negative_frequencies: bool
    plot_absolute_frequencies: bool
    plot_amplitude: bool
    plot_density: bool
    plot_cumulative_normalized: bool
    plot_style: _styleT
    plot_dB_scale: bool
    threaded_acquisition: bool
    reference_spectrum: _keyT
    processed_unit: str

    locals().update({attr: _forward_property(PlotManager, '_plot_manager', attr)
                     for attr in _to_expose})

    @check_literals
    def __init__(self, daq: Optional[DAQ] = None, *,
                 psd_estimator: Optional[Union[Callable, dict[str, Any]]] = None,
                 procfn: Optional[Union[Callable, Sequence[Callable]]] = None,
                 plot_raw: bool = False, plot_timetrace: bool = False,
                 plot_cumulative: bool = False, plot_negative_frequencies: bool = True,
                 plot_absolute_frequencies: bool = True, plot_amplitude: bool = True,
                 plot_density: bool = True, plot_cumulative_normalized: bool = False,
                 plot_style: _styleT = 'fast',
                 plot_update_mode: Optional[Literal['fast', 'always', 'never']] = None,
                 plot_dB_scale: bool = False, play_sound: bool = False,
                 audio_amplitude_normalization: Union[Literal["single_max"], float] = "single_max",
                 threaded_acquisition: bool = True, blocking_acquisition: bool = False,
                 purge_raw_data: bool = False, prop_cycle=None, savepath: _pathT = None,
                 relative_paths: bool = True, compress: bool = True, raw_unit: str = 'V',
                 processed_unit: Optional[str] = None, figure_kw: Optional[Mapping] = None,
                 subplot_kw: Optional[Mapping] = None, gridspec_kw: Optional[Mapping] = None,
                 legend_kw: Optional[Mapping] = None):

        self._data: dict[tuple[int, str], dict] = {}
        self._savepath: Optional[Path] = None
        self._acquiring = False
        self._stop_event = Event()
        self._datasaver = AsyncDatasaver('dill', compress)

        self.daq = daq
        self.procfn = chain(*procfn) if np.iterable(procfn) else chain(procfn or Id)
        self.relative_paths = relative_paths
        if savepath is None:
            savepath = Path.home() / 'python_spectrometer' / datetime.now().strftime('%Y-%m-%d')
        self.savepath = savepath
        if plot_update_mode is not None:
            warnings.warn('plot_update_mode is deprecated and has no effect', DeprecationWarning)
        if purge_raw_data:
            warnings.warn('Enabling purge raw data might break some plotting features!',
                          UserWarning)
        self.purge_raw_data = purge_raw_data
        self.threaded_acquisition = threaded_acquisition
        self.blocking_acquisition = blocking_acquisition

        if psd_estimator is None:
            psd_estimator = {}
        if callable(psd_estimator):
            self.psd_estimator = psd_estimator
        elif isinstance(psd_estimator, Mapping):
            self.psd_estimator = partial(welch, **psd_estimator)
        else:
            raise TypeError('psd_estimator should be callable or kwarg dict for welch().')

        uses_windowed_estimator = 'window' in inspect.signature(self.psd_estimator).parameters

        if self.daq is not None:
            complex_data = np.issubdtype(self.daq.DTYPE, np.complexfloating)
        else:
            complex_data = None

        self._plot_manager = PlotManager(self._data, plot_raw, plot_timetrace,
                                         plot_cumulative, plot_negative_frequencies,
                                         plot_absolute_frequencies, plot_amplitude,
                                         plot_density, plot_cumulative_normalized,
                                         plot_style, plot_dB_scale, prop_cycle, raw_unit,
                                         processed_unit, uses_windowed_estimator, complex_data,
                                         figure_kw, subplot_kw, gridspec_kw, legend_kw)

        self._audio_amplitude_normalization = audio_amplitude_normalization
        self._play_sound = play_sound

    def __repr__(self) -> str:
        if self.keys():
            return super().__repr__() + ' with keys\n' + self._repr_keys()
        else:
            return super().__repr__()

    def __getitem__(self, key: _keyT) -> dict[str, Any]:
        return self._data[self._parse_keys(key)[0]]

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterator (yields values instead of keys like a dict)."""
        yield from self.values()

    def __len__(self) -> int:
        return self._data.__len__()

    @property
    def _index(self) -> int:
        """Next available index."""
        known_ix = sorted((ix for ix, *_ in self._data))
        free_ix = (np.diff(known_ix) != 1).nonzero()[0]
        if 0 not in known_ix:
            return 0
        elif free_ix.size:
            return free_ix[0] + 1
        else:
            return len(self._data)

    @cached_property
    def _runfile(self) -> Path:
        return self._get_new_file('files', suffix='txt')

    @cached_property
    def _objfile(self) -> Path:
        return self._get_new_file('object', suffix='')

    @property
    def files(self) -> Generator[str, None, None]:
        """List of all data files."""
        return (str(data['filepath']) for data in self.values())

    @property
    def savepath(self) -> Path:
        """The base path where files are stored on disk."""
        return self._savepath

    @savepath.setter
    def savepath(self, path):
        self._savepath = io.to_global_path(path)

    @property
    def acquiring(self) -> bool:
        """Indicates if the spectrometer is currently acquiring data."""
        return self._acquiring

    @cached_property
    def audio_stream(self) -> WaveformPlaybackManager:
        """Manages audio waveform playback."""
        return WaveformPlaybackManager(amplitude_normalization=self.audio_amplitude_normalization)

    @property
    def play_sound(self):
        """Play the recorded noise sample out loud."""
        return self._play_sound

    @play_sound.setter
    def play_sound(self, flag:bool):
        if self._play_sound != flag:
            self._play_sound = flag
            # as the play back was deactivate, the stream might need to be stopped.
            # this will be done now:
            if not flag and 'audio_stream' in self.__dict__:
                del self.audio_stream

    @property
    def audio_amplitude_normalization(self):
        """The factor the waveform is divided by to normalize the waveform."""
        return self._audio_amplitude_normalization

    @audio_amplitude_normalization.setter
    def audio_amplitude_normalization(self, val):
        self._audio_amplitude_normalization = val
        if 'audio_stream' in self.__dict__:
            self.audio_stream.amplitude_normalization = val

    def _resolve_path(self, file: _pathT) -> Path:
        """Resolve file to a fully qualified path."""
        if not (file := Path(file)).is_absolute():
            file = self.savepath / file
        return io.to_global_path(file)

    def _get_new_file(self, append: str = 'data', comment: str = '', suffix: str = 'npz') -> Path:
        """Obtain a new file."""
        self.savepath.mkdir(parents=True, exist_ok=True)
        comment = _make_filesystem_compatible(comment)
        file = "spectrometer{}_{}{}{}".format('_' + append if append else '',
                                              datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                              '_' + comment if comment else '',
                                              '.' + suffix if suffix else '')
        if self.relative_paths:
            return Path(file)
        return self.savepath / file

    def _unravel_coi(self, *comment_or_index: _keyT) -> tuple[_keyT, ...]:
        if len(comment_or_index) == 1:
            if comment_or_index[0] == 'all':
                comment_or_index = tuple(self.keys())
            elif isinstance(comment_or_index[0], slice):
                idx = [ix for ix, _ in self.keys()]
                slc = cast(slice, comment_or_index[0])
                comment_or_index = tuple(ix for ix in range(max(idx) + 1)[slc] if ix in idx)
        return comment_or_index

    def _parse_keys(self, *comment_or_index: _keyT) -> list[tuple[int, str]]:
        """Get spectrum data for key."""
        parsed = []
        for coi in comment_or_index:
            if coi in self.keys():
                # key a tuple of (int, str)
                parsed.append(coi)
            else:
                # Check if key is either int or str, otherwise raise
                indices, comments = zip(*tuple(self._data))
                try:
                    if isinstance(coi, str):
                        ix = [i for i, elem in enumerate(comments) if elem == coi]
                        if len(ix) == 0:
                            raise ValueError
                        elif len(ix) == 1:
                            ix = ix[0]
                        else:
                            raise KeyError(f"Comment '{coi}' occurs multiple times. Please "
                                           + "specify the index.") from None
                    elif isinstance(coi, int):
                        # Allow for negative indices. Can raise ValueError
                        ix = indices.index(coi if coi >= 0 else len(indices) + coi)
                    else:
                        raise ValueError
                except ValueError:
                    raise KeyError(f'Key {coi} not registered') from None
                parsed.append((indices[ix], comments[ix]))
        return parsed

    def _repr_keys(self, *keys) -> str:
        if not keys:
            keys = self.keys()
        return ' - ' + '\n - '.join(str(key) for key in sorted(self.keys()) if key in keys)

    def _save(self, file: _pathT, **kwargs):
        self._datasaver(io.check_path_length(self._resolve_path(file)),
                        **_to_native_types(kwargs))

    @classmethod
    def _make_kwargs_compatible(cls, kwargs: dict[str, Any]) -> dict[str, Any]:
        compatible_kwargs = dict()
        signature = inspect.signature(cls)

        # Replace old param names by new ones ...
        for old, new in cls._OLD_PARAMETER_NAMES.items():
            if old in kwargs:
                if new not in kwargs:
                    kwargs[new] = kwargs.pop(old)
                else:
                    # Don't overwrite in case of clash
                    kwargs.pop(old)

        # And drop all other unknown ones.
        for param, val in kwargs.items():
            if param not in signature.parameters:
                warnings.warn(f'Parameter {param} not supported anymore, dropping', RuntimeWarning)
            else:
                compatible_kwargs[param] = val

        return compatible_kwargs

    def _assert_ready(self):
        if not isinstance(self.daq, DAQ):
            raise ReadonlyError('Cannot take new data since no DAQ backend given')
        if self.acquiring:
            raise RuntimeError('Spectrometer is currently acquiring.')

    def _process_data(self, timetrace_raw, **settings) -> dict[str, Any]:
        S_raw, f_raw, _ = welch(timetrace_raw, **settings)
        S_processed, f_processed, timetrace_processed = self.psd_estimator(
            self.procfn(np.array(timetrace_raw), **settings),
            **settings
        )
        # if read-only, self.daq is None
        DAQSettings = getattr(self.daq or daq_settings, 'DAQSettings')
        data = dict(timetrace_raw=timetrace_raw,
                    timetrace_processed=timetrace_processed,
                    f_raw=f_raw,
                    f_processed=f_processed,
                    S_raw=S_raw,
                    S_processed=S_processed,
                    settings=DAQSettings(settings))
        return data

    def _handle_fetched(self, key: _keyT, fetched_data, **settings):
        processed_data = self._process_data(fetched_data, **settings)

        # TODO: This could fail if the iterator was empty and processed_data was never assigned
        self._data[key].update(_merge_data_dicts(self._data[key], processed_data))
        self.set_reference_spectrum(self.reference_spectrum)
        if self._plot_manager.is_fig_open():
            self.show(key)
        else:
            raise KeyboardInterrupt('Spectrometer was closed before data acquisition finished')

    def _handle_final(self, key: _keyT, metadata: Any):
        if self.play_sound:
            self.play(key)

        if self.purge_raw_data:
            del self._data[key]['timetrace_raw']
            del self._data[key]['timetrace_processed']
            del self._data[key]['f_raw']
            del self._data[key]['S_raw']
            self._data[key]['S_processed'] = np.mean(self._data[key]['S_processed'], axis=0)[None]

        self._data[key].update(measurement_metadata=metadata)
        self._save(self._data[key]['filepath'], **self._data[key])

    def _take_threaded(self, progress: bool, key: _keyT, n_avg: int, **settings):
        """Acquire data in a separate thread.

        The :meth:`.daq.base.DAQ.acquire` iterator is incremented in a
        background thread and fed into a :class:`~queue.Queue`. The
        data is fetched and plotted in a callback that is periodically
        triggered by a timer connected to the figure.

        See Also
        --------
        :attr:`._plot_manager.PlotManager.timer`
        :attr:`._plot_manager.PlotManager.TIMER_INTERVAL`

        """

        def update_plot():
            try:
                result = queue.get(block=False)
            except Empty:
                return
            try:
                if isinstance(result, StopIteration):
                    self._handle_final(key, result.value)
                    self._acquiring = False
                    # Signal the timer that we've stopped. Removes the callback
                    return False
                elif isinstance(result, Exception):
                    # Make sure we are left in a reproducible state
                    self.drop(key)
                    self._acquiring = False
                    raise RuntimeError('Something went wrong during data acquisition') from result
                else:
                    self._handle_fetched(key, result, n_avg=n_avg, **settings)
            finally:
                queue.task_done()

        def acquire():
            iterator = self.daq.acquire(n_avg=n_avg, **settings)
            for i in progressbar(count(), disable=not progress, total=n_avg,
                                 desc=f'Acquiring {n_avg} spectra with key {key}'):
                if self._stop_event.is_set():
                    print('Acquisition interrupted.')
                    break
                try:
                    item = next(iterator)
                except Exception as error:
                    queue.put(error)
                    break
                else:
                    queue.put(item)

            # The plot_update callback does not run on a noninteractive backend,
            # so need to reset the flag at the thread's exit.
            if not INTERACTIVE:
                self._acquiring = False

        def on_close(event):
            self._stop_event.set()
            self._acquiring = False

        INTERACTIVE = is_using_mpl_gui_backend(self.fig)

        self._stop_event.clear()
        queue = Queue()
        thread = Thread(target=acquire, daemon=True)
        thread.start()

        # Stop data acquisition when the figure is closed
        self.fig.canvas.mpl_connect('close_event', on_close)

        # Run the timer that periodically checks for new data and updates the plot
        self._plot_manager.timer.add_callback(update_plot)
        self._plot_manager.timer.start()
        self._acquiring = True

    def _take_sequential(self, progress: bool, key: _keyT, n_avg: int, **settings):
        """Acquire data in the main thread."""
        # It's not necessary to set the _acquiring flag because this is
        # blocking anyway.
        iterator = self.daq.acquire(n_avg=n_avg, **settings)
        for _ in progressbar(count(), disable=not progress, total=n_avg,
                             desc=f'Acquiring {n_avg} spectra with key {key}'):
            try:
                fetched_data = next(iterator)
            except StopIteration as stop:
                self._handle_final(key, stop.value)
                break
            except Exception as error:
                # Make sure we are left in a reproducible state
                self.drop(key)
                raise RuntimeError('Something went wrong during data acquisition') from error
            else:
                self._handle_fetched(key, fetched_data, n_avg=n_avg, **settings)

    def take(self, comment: str = '', progress: bool = True, **settings):
        """Acquire a spectrum with given settings and comment.

        There are default parameter names that manage data acquisition
        settings by way of a dictionary subclass,
        :class:`.daq.settings.DAQSettings`. These are checked for
        consistency at runtime, since it is for example not possible to
        specify :attr:`~.daq.settings.DAQSettings.f_min` to be smaller
        than the frequency resolution
        :attr:`~.daq.settings.DAQSettings.df`. See the
        :class:`~.daq.settings.DAQSettings` docstring for examples; the
        special settings are reproduced below.

        Parameters
        ----------
        comment : str
            An explanatory comment that helps identify the spectrum.
        progress : bool
            Show a progressbar for the outer repetitions of data
            acqusition. Default True.
        **settings
            Keyword argument settings for the data acquisition and
            possibly data processing using :attr:`procfn` or
            :attr:`fourier_procfn`.
        """
        self._assert_ready()

        if (key := (self._index, comment)) in self._data:
            raise KeyError(f'Key {key} already exists. Choose a different comment.')

        # Drop density from settings so that self.psd_estimator will always return a PSD
        if 'density' in settings:
            settings.pop('density')

        settings = self.daq.DAQSettings(self.daq.setup(**settings))
        filepath = self._get_new_file(comment=comment)
        self._data[key] = {'settings': settings, 'comment': comment, 'filepath': filepath,
                           'timestamp': datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}
        # Make sure the figure is live
        self._plot_manager.update_figure()
        self._plot_manager.add_new_line_entry(key)

        if self.threaded_acquisition:
            self._take_threaded(progress, key, **settings)
        else:
            self._take_sequential(progress, key, **settings)
        if self.blocking_acquisition:
            self.block_until_ready()

    take.__doc__ = (take.__doc__.replace(8*' ', '')
                    + '\n\nDAQ Parameters'
                    + '\n==============\n'
                    + '\n'.join((f'{key} : {val}' for key, val in daq_settings._doc_.items())))

    def drop(self, *comment_or_index: _keyT, update_figure: bool = True):
        """Delete a spectrum from cache and plot.

        Parameters
        ----------
        *comment_or_index : int | str | (int, str)
            Key(s) for spectra. May be either the integer index, the
            string comment, or a tuple of both. See :meth:`print_keys`
            for all registered keys.
        update_figure : bool, default True
            Update the figure. Only used internally.

        See Also
        --------
        :meth:`hide`
        :meth:`show`

        Examples
        --------
        The following are equivalent for a :class:`Spectrometer` with
        keys ``[(0, 'a'), (1, 'b')]``::

            spect.drop(0)
            spect.drop('a')
            spect.drop(-2)
            spect.drop((0, 'a'))

        Multiple spectra can be dropped at the same time::

            spect.drop(0, (1, 'b'))

        """
        try:
            for key in self._parse_keys(*self._unravel_coi(*comment_or_index)):
                self._plot_manager.destroy_lines(keys=[key])
                self._plot_manager.drop_lines(key)
                del self._data[key]
                if key == self.reference_spectrum:
                    if self:
                        self._plot_manager._reference_spectrum = list(self.keys())[0]
                    else:
                        self._plot_manager._reference_spectrum = None
        finally:
            if update_figure:
                with self._plot_manager.plot_context:
                    self._plot_manager.update_figure()

    def delete(self, *comment_or_index: _keyT):
        """Delete the data of a spectrum saved on disk and drop it
        from cache.

        .. warning::
            This deletes data from disk!

        Parameters
        ----------
        *comment_or_index : int | str | (int, str)
            Key(s) for spectra. May be either the integer index, the
            string comment, or a tuple of both. See :meth:`print_keys`
            for all registered keys.

        """
        try:
            for key in self._parse_keys(*self._unravel_coi(*comment_or_index)):
                file = self[key]['filepath']
                if not file.is_absolute():
                    file = self.savepath / file
                if io.query_yes_no(f'Really delete file {file}?', default='no'):
                    self.drop(key, update_figure=False)
                    os.remove(file)
        finally:
            with self._plot_manager.plot_context:
                self._plot_manager.update_figure()

    def hide(self, *comment_or_index: _keyT):
        """Hide a spectrum in the plot.

        Parameters
        ----------
        *comment_or_index : int | str | (int, str) | slice | 'all'
            Key(s) for spectra. May be either the integer index, the
            string comment, or a tuple of both. See :meth:`print_keys`
            for all registered keys. Can also be 'all', which hides
            all registered spectra.

        See Also
        --------
        :meth:`drop`
        :meth:`show`

        Examples
        --------
        The following are equivalent for a :class:`Spectrometer` with
        keys ``[(0, 'a'), (1, 'b')]``::

            spect.hide(0)
            spect.hide('a')
            spect.hide(-2)
            spect.hide((0, 'a'))

        Multiple spectra can be hidden at the same time::

            spect.hide(0, (1, 'b'))

        """
        try:
            for key in self._parse_keys(*self._unravel_coi(*comment_or_index)):
                self._plot_manager.destroy_lines(keys=[key])
                self._plot_manager.update_line_attrs(self._plot_manager.plots_to_draw,
                                                     self._plot_manager.lines_to_draw,
                                                     [key], stale=False, hidden=True)
        finally:
            with self._plot_manager.plot_context:
                self._plot_manager.update_figure()

    def show(self, *comment_or_index: _keyT, color: Optional[Union[str, list[str]]] = None):
        """Show a spectrum in the plot.

        Parameters
        ----------
        *comment_or_index : int | str | (int, str) | slice | 'all'
            Key(s) for spectra. May be either the integer index, the
            string comment, or a tuple of both. See :meth:`print_keys`
            for all registered keys. Can also be 'all', which shows
            all registered spectra.
        color: str or list[str]
            A valid matplotlib color to override the default color for
            this key.

        See Also
        --------
        :meth:`drop`
        :meth:`hide`

        Examples
        --------
        The following are equivalent for a :class:`Spectrometer` with
        keys ``[(0, 'a'), (1, 'b')]``::

            spect.show(0)
            spect.show('a')
            spect.show(-2)
            spect.show((0, 'a'))

        Multiple spectra can be shown at the same time::

            spect.show(0, (1, 'b'))

        You can override the default color for the spectrum::

            spect.show(0, color='pink')
            spect.show(0, 1, color=['k', 'r'])

        """
        # Need to unravel 'all' or slice for colors below
        comment_or_index = self._unravel_coi(*comment_or_index)

        if color is not None:
            if colors.is_color_like(color):
                color = [color]
            assert len(color) == len(comment_or_index), 'Need as many colors as there are keys'
        else:
            color = [None]*len(comment_or_index)

        try:
            for key, col in zip(self._parse_keys(*comment_or_index), color):
                # Color kwarg needs to be set for all plot and line types
                # (also the ones not currently shown)
                self._plot_manager.update_line_attrs(keys=[key], color=col)
                self._plot_manager.update_line_attrs(self._plot_manager.plots_to_draw,
                                                     self._plot_manager.lines_to_draw,
                                                     [key], stale=True, hidden=False)
        finally:
            with self._plot_manager.plot_context:
                self._plot_manager.update_figure()

    def play(self, comment_or_index: _keyT, use_processed_timetrace: bool = False, min_duration: Union[None, float] = None):
        """Plays the noise out loud to allow the scientist to use their auditory input.

        Parameters
        ----------
        use_processed_timetrace : bool
            If true, then the 'timetrace_processed' data is used for the playback. If False is given, then 'timetrace_raw' is used. (default=False)
        min_duration : Union[None, float]
            The minimum duration that the noise is to be played. The sample will be repeated until the overall duration is equal to or larger than the min_duration.

        """

        key = self._parse_keys(comment_or_index)[0]

        fs = self._data[key]['settings'].fs
        dt = 1/fs

        if use_processed_timetrace:
            data = self._data[key]['timetrace_processed'][-1]
        else:
            data = self._data[key]['timetrace_raw'][-1]

        original_duration = dt*len(data) # in s

        # taking the real component of the signal if a complex numpy array is given
        if np.iscomplexobj(data):
            data = np.abs(data)

        # repeat the wave to go up to the min_duration
        if min_duration is not None:
            repetitions = np.ceil(min_duration/original_duration)
            if repetitions > 1:
                data = np.repeat(data[None, :], repetitions, axis=0).flatten()

        self.audio_stream.notify(data.flatten().astype("float32"), fs)

    def live_view(
            self,
            max_rows: int = 50,
            in_process: bool = False,
            live_view_kw: Optional[Mapping] = None,
            **settings
    ) -> list[Union[FrequencyLiveView, TimeLiveView, live_view.LiveViewBase.LiveViewProxy]]:
        """Continuously acquire and live-plot spectra.

        .. note::
            This method does not save data to disk or to the internal
            cache.

        This always displays the power spectral density (PSD) of the
        signal, regardless of the settings respected by :meth:`take`.
        If :attr:`plot_timetrace` is ``True``, then the processed time
        traces are also shown in a separate live plot.

        Parameters
        ----------
        max_rows :
            Maximum number of time traces to display in the waterfall
            plot.
        in_process :
            Run the live view(s) in a separate process instead of the
            main process. This can improve performance / responsiveness
            but provides less control.
        live_view_kw :
            Optional keyword arguments passed to the
            :class:`~qutil:qutil.plotting.live_view.LiveViewBase` class.
        **settings :
            Acquisition settings. See :meth:`take`.

        See Also
        --------
        :meth:`take`

        """
        # TODO: Instead of setting up separate LiveView's for time and frequency
        #       data, the cleaner option would arguably be to subclass and add
        #       another subplot.
        # TODO: When plot_timetrace=True and one view is paused, closing a
        #       figure causes the thread to not join.

        self._assert_ready()

        # Since (up to) two views need to obtain data from a single source, we feed the data
        # into separate queues from a third thread. The views then obtain the data from those
        # queues (and put it into their own queues in their own thread).
        def put_frequency_data(put_queue: Queue, stop_event: Event, *, get_queue: LifoQueue, **_):
            t = np.arange(0, max_rows * T, T)
            while not stop_event.is_set():
                # get_queue is a LifoQueue, so we always get the freshest item
                S, f, _ = get_queue.get()
                put_queue.put((f, t, np.sqrt(S, out=S)))
                get_queue.task_done()
                # Flush all remaining items that might have been put
                live_view.flush_queue(get_queue)

        def put_time_data(put_queue: Queue, stop_event: Event, *, get_queue: LifoQueue, **_):
            t = np.linspace(0, T, settings['n_pts'])
            while not stop_event.is_set():
                *_, yt = get_queue.get()
                if np.issubdtype(self.daq.DTYPE, np.complexfloating):
                    put_queue.put((t, {'X': yt.real, 'Y': yt.imag}))
                else:
                    put_queue.put((t, yt))
                get_queue.task_done()
                live_view.flush_queue(get_queue)

        def acquire_and_feed(stop_event: Event, *queues: LifoQueue):
            """Acquire data and distribute it into the queue(s) from
            which the live views obtain the data."""
            for i, data in enumerate(self.daq.acquire(**settings)):
                S, f, yt = self.psd_estimator(self.procfn(np.array(data), **settings), **settings)
                for queue in queues:
                    # Make sure there's no race conditions by providing a copy to each view
                    queue.put(tuple(map(copy.copy, (S, f, yt))))

                # Set exit condition at the end so that acquired data is always processed.
                if stop_event.is_set():
                    break

        def monitor_event(get_event: Event, *set_events: Optional[Event]):
            """Observe if a view's stop flag has been set. If so, notify
            the other threads to stop as well."""
            get_event.wait()
            for event in set_events:
                if event is not None:
                    event.set()
            self._acquiring = False

        def get_live_view(cls, *args, **kwargs):
            if not in_process:
                return cls(*args, **kwargs)
            else:
                kwargs.setdefault('context_method',
                                  'forkserver' if platform.system() == 'Linux' else None)
                return getattr(cls, 'in_process')(*args, **kwargs)

        # Drop density from settings so that self.psd_estimator will always return a PSD
        settings.pop('density', None)
        settings['n_avg'] = 1_000_000
        if self.daq.__module__ == 'atsaverage':
            warnings.warn('This feature is untested with atsaverage. Proceed with care.',
                          UserWarning)

        settings = self.daq.setup(**settings)
        T = settings['n_pts'] / settings['fs']

        if np.issubdtype(self.daq.DTYPE, np.complexfloating) and self.plot_negative_frequencies:
            freq_xscale = _asinh_scale_maybe()
            xlim = np.array([-settings['f_max'], settings['f_max']])
        else:
            freq_xscale = 'log'
            xlim = np.array([settings['f_min'], settings['f_max']])
        if self.plot_absolute_frequencies:
            xlim += settings.get('freq', 0)

        if live_view_kw is None:
            live_view_kw = {}

        live_view_kw.setdefault('blocking_queue', True)
        live_view_kw.setdefault('autoscale_interval_ms', None)
        live_view_kw.setdefault('style', self.plot_style)
        live_view_kw.setdefault(
            'plot_legend',
            'upper right' if np.issubdtype(self.daq.DTYPE, np.complexfloating) else False
        )

        fixed_kw = dict(
            plot_line=True, xlim=xlim, ylim=(0, (max_rows - 1) * T),
            xlabel='$f$', ylabel='$t$', clabel='$S(f)$',
            units={'x': 'Hz', 'y': 's', 'c': self.processed_unit + r'$/\sqrt{{\mathrm{{Hz}}}}$'},
            img_kw=dict(norm=colors.LogNorm(vmin=0.1, vmax=10))
        )
        freq_kw = {'autoscale': 'c', 'xscale': freq_xscale, 'img_kw': {'cmap': 'Blues'}}
        freq_kw = _merge_recursive(freq_kw, _merge_recursive(live_view_kw, fixed_kw))
        if not _dict_is_subset(live_view_kw, freq_kw):
            warnings.warn('Overrode some keyword arguments for FrequencyLiveView', UserWarning)

        # The view(s) get data from these queues and subsequently put them into their own
        self._stop_event.clear()
        get_queues = [LifoQueue(maxsize=int(live_view_kw['blocking_queue']))]
        views = [get_live_view(FrequencyLiveView, put_frequency_data, get_queue=get_queues[0],
                               **freq_kw)]

        if self.plot_timetrace:
            fixed_kw = dict(xlim=(0, T), xlabel='$t$', ylabel='Amplitude',
                            n_lines=2 if np.issubdtype(self.daq.DTYPE, np.complexfloating) else 1,
                            units={'x': 's', 'y': self.processed_unit})
            time_kw = {'autoscale': 'y'}
            time_kw = _merge_recursive(time_kw, _merge_recursive(live_view_kw, fixed_kw))
            if not _dict_is_subset(live_view_kw, time_kw):
                warnings.warn('Overrode some keyword arguments for TimeLiveView', UserWarning)

            get_queues.append(LifoQueue(maxsize=int(live_view_kw['blocking_queue'])))
            views.append(get_live_view(TimeLiveView, put_time_data, get_queue=get_queues[1],
                                       **time_kw))

            # The watcher threads monitor the views if they were stopped and notify the feeder
            # thread (and stop the other view)
            watcher_threads = [
                Thread(target=monitor_event,
                       args=(views[0].stop_event, self._stop_event, views[1].stop_event,
                             # Need to add the proxy's close_event for headless tests
                             views[1].close_event if in_process else None),
                       daemon=True),
                Thread(target=monitor_event,
                       args=(views[1].stop_event, self._stop_event, views[0].stop_event,
                             views[0].close_event if in_process else None),
                       daemon=True),
            ]
        else:
            watcher_threads = [
                Thread(target=monitor_event, args=(views[0].stop_event, self._stop_event),
                       daemon=True)
            ]

        # The feeder thread actually performs the data acquisition and distributes it into the
        # get_queues until stop_event is set.
        feeder_thread = Thread(target=acquire_and_feed, args=[self._stop_event] + get_queues,
                               daemon=True)

        # Finally, start all the threads
        feeder_thread.start()
        for watcher in watcher_threads:
            watcher.start()

        for view in views:
            if not in_process:
                view.start()
            else:
                view.block_until_ready()

        self._acquiring = True
        return views

    def block_until_ready(self, timeout: float = float('inf')):
        """Block the interpreter until acquisition is complete.

        This is a convenience function to ensure all GUI events are
        processed before another acquisition is started.

        Spins the event loop to allow the figure to remain responsive.

        Parameters
        ----------
        timeout :
            Optionally specify a timeout after which a :class:`TimeoutError`
            is raised.
        """
        with misc.timeout(timeout, raise_exc=True) as exceeded:
            while self.acquiring and not exceeded:
                self.fig.canvas.start_event_loop(self._plot_manager.TIMER_INTERVAL * 1e-3)

    def abort_acquisition(self):
        """Abort the current acquisition."""
        self._stop_event.set()

    def reprocess_data(self,
                       *comment_or_index: _keyT,
                       save: Literal[False, True, 'overwrite'] = False,
                       processed_unit: Optional[str] = None,
                       **new_settings):
        """Repeat data processing using updated settings.

        .. warning::
            This can change data saved on disk!

        Parameters
        ----------
        *comment_or_index : int | str | (int, str) | slice | 'all'
            Key(s) for spectra. May be either the integer index, the
            string comment, or a tuple of both. See :meth:`print_keys`
            for all registered keys. Can also be 'all', which processes
            all registered spectra.
        save : bool or 'overwrite', default False
            Save the processed data to a new or overwrite the old file.
        processed_unit : str, optional
            A string for the new unit if it changes.
        **new_settings
            Updated keyword argument settings for data processing using
            :attr:`procfn` or :attr:`fourier_procfn`. Previous settings
            are used for those not provided here.
            Note that, in offline mode (without a ``DAQ`` instance
            attached), settings are only validated with the bare
            :class:`daq_settings.DAQSettings` class which might not
            consider all constraints.
        """
        try:
            for key in self._parse_keys(*self._unravel_coi(*comment_or_index)):
                data = self._data[key]
                if self.daq is not None:
                    settings = self.daq.DAQSettings(data['settings'] | new_settings)
                else:
                    settings = daq_settings.DAQSettings(data['settings'] | new_settings)
                data.update(self._process_data(self._data[key]['timetrace_raw'],
                                               **settings.to_consistent_dict()))

                if save:
                    if save == 'overwrite':
                        data['filepath'] = io.query_overwrite(data['filepath'])
                    else:
                        data['filepath'] = self._get_new_file(comment=data['comment'])
                    self._datasaver(data['filepath'], **data)

                self._data[key] = data
                self._plot_manager.update_line_attrs(self._plot_manager.plots_to_draw,
                                                     self._plot_manager.lines_to_draw,
                                                     keys=[key], stale=True)
        finally:
            if processed_unit is not None:
                self._plot_manager.processed_unit = str(processed_unit)
                self._plot_manager.setup_figure()
            else:
                with self._plot_manager.plot_context:
                    self._plot_manager.update_figure()

    def set_reference_spectrum(self, comment_or_index: Optional[_keyT] = None):
        """Set the spectrum to be taken as a reference for the dB scale.

        Applies only if :attr:`plot_dB_scale` is True."""
        # Cannot implement this as a setter for the reference_spectrum propert
        # since we need the _parse_keys method of Spectrometer.
        if comment_or_index is None:
            # Default for no data
            if self._data:
                comment_or_index = 0
            else:
                return
        key = self._parse_keys(comment_or_index)[0]
        if key != self.reference_spectrum:
            self._plot_manager.reference_spectrum = key
            if self.plot_dB_scale:
                self._plot_manager.update_line_attrs(['main', 'cumulative'],
                                                     self._plot_manager.lines_to_draw,
                                                     stale=True)
            if self._plot_manager.is_fig_open():
                self._plot_manager.setup_figure()

    @staticmethod
    def update_metadata(file: _pathT, *,
                        delete_old_file: bool = False,
                        new_comment: Optional[str] = None,
                        new_settings: Optional[Mapping[str, Any]] = None,
                        new_savepath: Union[Literal[False], _pathT] = False,
                        relative_paths: bool = True,
                        compress: bool = True):
        """Update the metadata of a previously acquired spectrum and
        write it to disk.

        .. warning::
            This can change data saved on disk!

        Parameters
        ----------
        file: PathLike
            The data file to modify.
        delete_old_file : bool
            Rename the file on disk according to the updated comment.
            If false, a new file is written and the old retained.
            Default: False.

            .. note::
                The new file will have the same timestamp but possibly
                a different comment and therefore filename. Thus, any
                old serialization files will have dead filename links
                generated by :meth:`save_run` and you should
                re-serialize the object.

        new_comment : str
            A new comment replacing the old one.
        new_settings : Mapping[str, Any]
            New (metadata) settings to add to/replace existing ones.

            .. warning::
                This might overwrite settings used for spectral
                estimation. In some cases, it might be better to delete
                the previous spectrum from disk and acquire a new one.

        new_savepath : False | PathLike, default: False
            Use this object's savepath or a specified one instead of
            the one stored in the file. Helpful for handling data
            that has been moved to a different system in case absolute
            paths were used.
        relative_paths: bool
            Use relative or absolute file paths.
        compress : bool
            Compress the data.
        """
        data = _load_spectrum(oldfile := io.to_global_path(file).with_suffix('.npz'))

        if new_savepath is False:
            savepath = oldfile.parent
        else:
            savepath = Path(cast(_pathT, new_savepath))
        if new_comment is not None:
            data['comment'] = new_comment
        if new_settings is not None:
            data['settings'].update(new_settings)
        newfile = (
            # trunk and timestamp parts of the filename
            oldfile.stem[:37]
            # new comment tail
            + (('_' + _make_filesystem_compatible(data['comment'])) if data['comment'] else '')
        )
        data['filepath'] = newfile if relative_paths else savepath / newfile

        newfile = io.query_overwrite(io.check_path_length(savepath / newfile))
        with AsyncDatasaver('dill', compress) as datasaver:
            datasaver.save_sync(savepath / newfile, **_to_native_types(data))

        if newfile == oldfile:
            # Already 'deleted' (overwrote) the old file
            return
        if delete_old_file and io.query_yes_no(f"Really delete file {file}?", default='no'):
            os.remove(file)

    def save_run(self, file: Optional[_pathT] = None, verbose: bool = False) -> Path:
        """Saves the names of all data files to a text file."""
        if file := self._resolve_path(file):
            file = file.with_stem(file.stem + '_files').with_suffix('.txt')
        else:
            file = self._runfile
        file = io.check_path_length(file)
        file.write_text('\n'.join(self.files))
        if verbose:
            print(f'Wrote filenames to {file}.')

        if self.relative_paths:
            return file.relative_to(self.savepath)
        return file

    @mock.patch.multiple('shelve', Unpickler=_Unpickler, Pickler=dill.Pickler)
    def serialize_to_disk(self, file: Optional[_pathT] = None, protocol: int = -1,
                          verbose: bool = False):
        """Serialize the Spectrometer object to disk.

        Parameters
        ----------
        file : str | Path
            Where to save the data. Defaults to the same directory where
            also the spectral data is saved.
        protocol : int
            The pickle protocol to use.
        verbose : bool
            Print some progress updates.

        See Also
        --------
        :meth:`recall_from_disk`
        """
        if file is None:
            file = self._objfile
        file = io.check_path_length(
            io.query_overwrite(_resolve_shelve_file(self._resolve_path(file)))
        ).with_suffix('')

        spectrometer_attrs = ['psd_estimator', 'procfn', 'savepath', 'relative_paths',
                              'plot_raw', 'plot_timetrace', 'plot_cumulative',
                              'plot_negative_frequencies', 'plot_absolute_frequencies',
                              'plot_amplitude', 'plot_density', 'plot_cumulative_normalized',
                              'plot_style', 'plot_update_mode', 'plot_dB_scale']
        plot_manager_attrs = ['reference_spectrum', 'prop_cycle', 'raw_unit', 'processed_unit']
        with shelve.open(str(file), protocol=protocol) as db:
            # Constructor args
            for attr in spectrometer_attrs:
                try:
                    db[attr] = getattr(self, attr)
                except AttributeError:
                    pass
            for attr in plot_manager_attrs:
                try:
                    db[attr] = getattr(self._plot_manager, attr)
                except AttributeError:
                    pass
            # Write a text file with the locations of all data files
            db['runfile'] = self.save_run(file, verbose=verbose)
        if verbose:
            print(f'Wrote object data to {file}')

    @classmethod
    @mock.patch.multiple('shelve', Unpickler=_Unpickler, Pickler=dill.Pickler)
    def recall_from_disk(cls, file: _pathT, daq: Optional[DAQ] = None, *,
                         reprocess_data: bool = False, savepath: Optional[_pathT] = None,
                         **new_settings):
        """Restore a Spectrometer object from disk.

        Parameters
        ----------
        file : str | Path
            The saved file.
        daq : DAQ
            The :class:`.DAQ` instance that sets up and executes data
            acquisition (see also the class constructor).

            If not given, the instance is read-only and can only be used
            for processing and plotting old data.
        reprocess_data : bool
            Redo the processing steps using this object's :attr:`procfn`
            and :attr:`psd_estimator`. Default: False.
        savepath : str | Path
            Overrides the savepath where data files are found.

        See Also
        --------
        :meth:`serialize_to_disk`
        """

        if not (file := _resolve_shelve_file(io.to_global_path(file))).exists():
            raise FileNotFoundError(f'File {file} does not exist!')
        with shelve.open(str(file.with_suffix(''))) as db:
            if not db:
                raise FileNotFoundError(f'File {file} is empty!')
            try:
                kwargs = dict(**db)
            except TypeError:
                # Weirdly, if a serialized function object does not exist in the
                # namespace, a TypeError is raised instead of complaining about
                # said object. Therefore, go through the db one-by-one to trigger
                # the error on the object actually causing problems
                kwargs = dict()
                for key, val in db.items():
                    kwargs[key] = val

            if savepath is not None:
                kwargs['savepath'] = io.to_global_path(savepath)
            if not (runfile := kwargs.pop('runfile')).is_absolute():
                runfile = kwargs['savepath'] / runfile
            spectrum_files = np.array(io.to_global_path(runfile).read_text().split('\n'))

        # Need to treat reference_spectrum separately since it is not a
        # Spectrometer but a _PlotManager attribute.
        reference_spectrum = kwargs.pop('reference_spectrum', None)

        spectrometer = cls(daq=daq, **cls._make_kwargs_compatible(kwargs))

        # Then restore the data
        keys = []
        for i, file in enumerate(progressbar(spectrum_files, desc='Loading files')):
            try:
                if spectrometer.relative_paths:
                    file = spectrometer.savepath / file
                keys.append(spectrometer.add_spectrum_from_file(file, show=False,
                                                                reprocess_data=reprocess_data,
                                                                **new_settings))
            except FileNotFoundError:
                print(f'Could not retrieve file {file}. Skipping.')

        try:
            spectrometer.set_reference_spectrum(reference_spectrum)
        except KeyError:
            warnings.warn('Could not set reference spectrum. Setting to key 0.', RuntimeWarning)
            spectrometer.set_reference_spectrum(0)

        # Show all at once to save drawing time
        spectrometer.show(*keys)
        return spectrometer

    def add_spectrum_from_file(self, file: _pathT, show: bool = True, color: Optional[str] = None,
                               reprocess_data: bool = False, **new_settings) -> tuple[int, str]:
        """Load data from disk and display it in the current figure.

        Parameters
        ----------
        file : str | os.PathLike
            The file to be loaded.
        show : bool
            Show the added spectrum in the plot.
        color : str
            A custom color to be used for the spectrum.
        reprocess_data : bool
            Redo the processing steps using this object's :attr:`procfn`
            and :attr:`psd_estimator`. Default: False.
        **new_settings
            New settings to use for reprocessing the data.

        Returns
        -------
        key : Tuple[int, str]
            The key assigned to the new spectrum data.

        """
        data = _load_spectrum(self._resolve_path(file).with_suffix('.npz'))

        if reprocess_data:
            data.update(self._process_data(data['timetrace_raw'],
                                           **{**data['settings'], **new_settings}))

        key = (self._index, data['comment'])
        self._data[key] = data
        # Make sure the figure is live
        self._plot_manager.update_figure()
        self._plot_manager.add_new_line_entry(key)
        if show:
            self.show(key, color=color)
        else:
            # Sets flags correctly
            self.hide(key)
        return key

    def print_settings(self, comment_or_index: _keyT):
        """Convenience method to pretty-print the settings for a
        previously acquired spectrum."""
        key = self._parse_keys(comment_or_index)[0]
        print(f'Settings for key {key}:')
        pprint(self[key]['settings'], width=120)

    def print_keys(self, *comment_or_index: _keyT):
        """Prints the registered (index, comment) tuples."""
        print(self._repr_keys(*self._parse_keys(*comment_or_index)))

    def keys(self) -> list[tuple[int, str]]:
        """Registered keys (sorted)."""
        return sorted(self._data.keys())

    def values(self) -> list[dict[str, Any]]:
        """Registered data (sorted by keys)."""
        return [value for _, value in sorted(self._data.items())]

    def items(self) -> list[tuple[tuple[int, str], dict[str, Any]]]:
        """Registered (key, data) tuples (sorted by keys)."""
        return [(key, value) for key, value in sorted(self._data.items())]


def _load_spectrum(file: _pathT) -> dict[str, Any]:
    """Loads data from a spectrometer run."""
    class monkey_patched_io:
        # Wrap around data saved during JanewayPath folly
        class JanewayWindowsPath(os.PathLike):
            def __init__(self, *args):
                self.path = Path(*args)

            def __fspath__(self):
                return str(self.path)

        def __enter__(self):
            setattr(io, 'JanewayWindowsPath', self.JanewayWindowsPath)

        def __exit__(self, exc_type, exc_val, exc_tb):
            delattr(io, 'JanewayWindowsPath')

    # Patch modules for data saved before move to separate package
    renamed_modules = {'qutil.measurement.spectrometer.daq.settings': daq_settings}
    target = 'pathlib._local' if sys.version_info >= (3, 13) else 'pathlib'
    PATHTYPE = type(Path())

    with (
            mock.patch.dict(sys.modules, renamed_modules),
            mock.patch.multiple(target, WindowsPath=PATHTYPE, PosixPath=PATHTYPE),
            np.load(file, allow_pickle=True) as fp,
            monkey_patched_io()
    ):
        data = {}
        for key, val in fp.items():
            try:
                # Squeeze singleton arrays into native Python data type
                data[key] = val.item()
            except ValueError:
                data[key] = val
            except Exception as err:
                raise RuntimeError(f'Encountered unhandled object in file {file}') from err

    return _from_native_types(data)


def _make_filesystem_compatible(comment: str) -> str:
    for old, new in zip((' ', '/', '.', ':', '\\', '|', '*', '?', '<', '>'),
                        ('_', '_', '-', '-', '_', '_', '_', '_', '_', '_')):
        comment = comment.replace(old, new)
    return comment


def _merge_data_dicts(data: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
    for key, val in new_data.items():
        if key == 'settings' or key.startswith('f'):
            # Only store single copy of frequency arrays / settings
            data[key] = val
        else:
            if key not in data:
                data[key] = []
            # Append new data arrays to list of existing
            data[key].append(val)
    return data


def _resolve_shelve_file(path: Path) -> Path:
    # shelve writes a single file without suffix or three files with suffixes
    # .dat, .dir, .bak depending on the dbm implementation available.
    if (p := path.with_suffix('')).is_file():
        return p
    if (p := path.with_suffix('.dat')).is_file():
        return p
    return path


def _to_native_types(data: dict[str, Any]) -> dict[str, Any]:
    """Converts custom types to native Python or NumPy types."""
    data_as_native_types = dict()
    for key, val in data.items():
        if isinstance(val, Path):
            # Cannot instantiate WindowsPaths on Posix and vice versa
            data_as_native_types[key] = str(val)
        elif isinstance(val, daq_settings.DAQSettings):
            # DAQSettings might not be available on system loading the
            # data, so unravel to consistent Python dict.
            data_as_native_types[key] = val.to_consistent_dict()
        else:
            data_as_native_types[key] = val
    return data_as_native_types


def _from_native_types(data: dict[str, Any]) -> dict[str, Any]:
    """Inverts :func:`_to_native_types`."""
    for key, val in data.items():
        if key == 'filepath':
            data[key] = Path(data[key])
        elif key == 'settings':
            data[key] = daq_settings.DAQSettings(data[key])
        else:
            data[key] = val
    return data


def _merge_recursive(orig: dict, upd: dict, inplace: bool = False) -> dict:
    """Recursively update the original dictionary 'orig' with the
    values from 'upd'.

    If both dictionaries have a value for the same key and those values
    are also dictionaries, the function is called recursively on those
    nested dictionaries.

    Parameters
    ----------
    orig :
        The dictionary that is updated.
    upd :
        The dictionary whose values are used for updating.
    inplace :
        Merge or update.

    Returns
    -------
    dict :
        The updated original dictionary.
    """
    if not inplace:
        orig = copy.copy(orig)

    for key, upd_value in upd.items():
        orig_value = orig.get(key)
        # If both the existing value and the update value are dictionaries,
        # merge them recursively.
        if isinstance(orig_value, dict) and isinstance(upd_value, dict):
            # Since `orig[key]` is already part of the copied version
            # if not inplace, we can update it in place.
            _merge_recursive(orig_value, upd_value, inplace=True)
        else:
            # Otherwise, replace or add the value from `upd` into `orig`.
            orig[key] = upd_value
    return orig


def _dict_is_subset(source: dict, target: dict) -> bool:
    """
    Checks recursively whether the nested dict *source* is a subset of
    *target*.

    Parameters
    ----------
    source :
        The dictionary whose keys must be present.
    target :
        The dictionary to check for the required keys.

    """
    for key, source_value in source.items():
        # Check if the key exists in the target dictionary.
        if key not in target:
            return False

        target_value = target[key]
        # If both values are dictionaries, check recursively.
        if isinstance(source_value, dict):
            if not isinstance(target_value, dict):
                return False
            if not _dict_is_subset(source_value, target_value):
                return False
        else:
            # For non-dict values, check equality.
            if source_value != target_value:
                return False

    return True


class ReadonlyError(Exception):
    """Indicates a :class:`Spectrometer` object is read-only."""
    pass
