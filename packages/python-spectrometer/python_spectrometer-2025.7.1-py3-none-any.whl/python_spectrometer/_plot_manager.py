"""This module defines the PlotManager helper class."""
import contextlib
import os
import sys
import warnings
import weakref
from collections.abc import Iterable, Mapping
from typing import (Any, Callable, ContextManager, Dict, List, Literal, Optional, Tuple, TypeVar,
                    Union)

import matplotlib.pyplot as plt
import numpy as np
from cycler import Cycler, cycler
from matplotlib import gridspec, scale
from qutil.functools import wraps
from qutil.itertools import compress
from qutil.misc import filter_warnings
from qutil.plotting import assert_interactive_figure
from scipy import integrate, signal

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

_T = TypeVar('_T')
_P = ParamSpec('_P')
_keyT = Union[int, str, tuple[int, str]]
_styleT = Union[str, os.PathLike, dict]
_styleT = Union[None, _styleT, list[_styleT]]


def with_plot_context(meth: Callable[_P, _T]) -> Callable[_P, _T]:
    @wraps(meth)
    def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        self, *args = args
        with self.plot_context:
            return meth(self, *args, **kwargs)

    return wrapped


class PlotManager:
    __instances = weakref.WeakSet()

    # TODO: blit?
    PLOT_TYPES = ('main', 'cumulative', 'time')
    LINE_TYPES = ('processed', 'raw')
    TIMER_INTERVAL: int = 20  # ms

    def __init__(self, data: dict[_keyT, Any], plot_raw: bool = False,
                 plot_timetrace: bool = False, plot_cumulative: bool = False,
                 plot_negative_frequencies: bool = True, plot_absolute_frequencies: bool = True,
                 plot_amplitude: bool = True, plot_density: bool = True,
                 plot_cumulative_normalized: bool = False, plot_style: _styleT = 'fast',
                 plot_dB_scale: bool = False, prop_cycle=None, raw_unit: str = 'V',
                 processed_unit: Optional[str] = None, uses_windowed_estimator: bool = True,
                 complex_data: Optional[bool] = False, figure_kw: Optional[Mapping] = None,
                 subplot_kw: Optional[Mapping] = None, gridspec_kw: Optional[Mapping] = None,
                 legend_kw: Optional[Mapping] = None):
        """A helper class that manages plotting spectrometer data."""
        self._data = data

        # settable properties exposed to Spectrometer
        self._plot_raw = plot_raw
        self._plot_timetrace = plot_timetrace
        self._plot_cumulative = plot_cumulative
        self._plot_negative_frequencies = plot_negative_frequencies
        self._plot_absolute_frequencies = plot_absolute_frequencies
        self._plot_amplitude = plot_amplitude
        self._plot_density = plot_density
        self._plot_cumulative_normalized = plot_cumulative_normalized
        self._plot_dB_scale = plot_dB_scale
        self._processed_unit = processed_unit if processed_unit is not None else raw_unit
        self._prop_cycle = prop_cycle
        # Use the setter to validate the style
        self._plot_style = None

        # For dB scale plots, default to the first spectrum acquired.
        self._reference_spectrum: Optional[_keyT] = None

        self.raw_unit = raw_unit
        self.uses_windowed_estimator = uses_windowed_estimator
        self._complex_data = complex_data

        self._fig = None
        self._leg = None
        self._timer = None
        self.axes = {key: dict.fromkeys(self.LINE_TYPES) for key in self.PLOT_TYPES}
        self.lines = dict()
        self.figure_kw = figure_kw or dict()
        self.subplot_kw = subplot_kw or dict()
        self.gridspec_kw = gridspec_kw or dict()
        self.legend_kw = legend_kw or dict()

        self.legend_kw.setdefault('loc', 'upper right')
        self.figure_kw.setdefault('num', f'Spectrometer {len(self.__instances) + 1}')
        if self.subplot_kw.pop('sharex', None) is not None:
            warnings.warn('sharex in subplot_kw not negotiable, dropping', UserWarning)

        # Set this last because it needs access to lines etc
        self.plot_style = plot_style

        # Keep track of instances that are alive for figure counting
        self.__instances.add(self)
        # TODO: this somehow never executes
        weakref.finalize(self, self.__instances.discard, self)

    def is_fig_open(self) -> bool:
        """Is the figure currently open, pending all events?"""
        # Need to flush possible close events before we can be sure!
        if self._fig is not None:
            self._fig.canvas.flush_events()
        return self._fig is not None and plt.fignum_exists(self.figure_kw['num'])

    @property
    @with_plot_context
    def fig(self):
        """The figure hosting the plots."""
        if self.is_fig_open():
            return self._fig
        elif plt.fignum_exists(num := self.figure_kw['num']):
            plt.figure(num).clear()

        try:
            self._fig = plt.figure(**self.figure_kw)
        except TypeError:
            if layout := self.figure_kw.pop('layout', None) is not None:
                # matplotlib < 3.5 doesn't support layout kwarg yet
                self.figure_kw[f'{layout}_layout'] = True
            elif layout is False:
                raise
            self._fig = plt.figure(**self.figure_kw)

        assert_interactive_figure(self._fig)

        def on_close(event):
            self._fig = None

            if self._timer is not None:
                self._timer.stop()
                self._timer = None

            # Clean up possible leftovers from before.
            self.destroy_axes()
            self.update_line_attrs(self.plots_to_draw, self.lines_to_draw, self.shown, stale=True)

        # If the window is closed, remove the figure from the cache so that it can be
        # recreated and stop the timer to delete any remaining callbacks
        self._fig.canvas.mpl_connect('close_event', on_close)

        self.setup_figure()
        return self._fig

    @property
    def timer(self):
        """A timer object associated with the figure."""
        if self._timer is None:
            self._timer = self.fig.canvas.new_timer(self.TIMER_INTERVAL)
        return self._timer

    @property
    def ax(self):
        """The axes hosting processed lines."""
        return np.array([val['processed'] for val in self.axes.values()
                         if val['processed'] is not None])

    @property
    def ax_raw(self):
        """The axes hosting raw lines."""
        return np.array([val['raw'] for val in self.axes.values()
                         if val['raw'] is not None])

    @property
    def leg(self):
        """Axes legend."""
        return self._leg

    @property
    def shown(self) -> tuple[tuple[int, str], ...]:
        return tuple(key for key, val in self.lines.items()
                     if val['main']['processed']['hidden'] is False)

    @property
    def lines_to_draw(self) -> tuple[str, ...]:
        return self.LINE_TYPES[:1 + self.plot_raw]

    @property
    def plots_to_draw(self) -> tuple[str, ...]:
        return tuple(compress(self.PLOT_TYPES, [True, self.plot_cumulative, self.plot_timetrace]))

    @property
    @with_plot_context
    def prop_cycle(self) -> Cycler:
        """The matplotlib property cycle.

        Set using either a :class:`cycler.Cycler` instance or a key-val
        mapping of properties.
        """
        return self._prop_cycle or plt.rcParams['axes.prop_cycle']

    @prop_cycle.setter
    def prop_cycle(self, val: Union[Mapping, Cycler]):
        if isinstance(val, Cycler):
            self._prop_cycle = cycler(val)
        else:
            self._prop_cycle = cycler(**val)

    @property
    def plot_context(self) -> ContextManager:
        if self.plot_style is not None:
            return plt.style.context(self.plot_style, after_reset=True)
        else:
            return contextlib.nullcontext()

    @property
    def plot_raw(self) -> bool:
        """If the raw data is plotted on a secondary y-axis."""
        return self._plot_raw

    @plot_raw.setter
    def plot_raw(self, val: bool):
        val = bool(val)
        if val != self._plot_raw:
            self._plot_raw = val
            self.update_line_attrs(self.plots_to_draw, ['raw'], stale=True, hidden=not val)
            if self.is_fig_open():
                # Only update the figure if it's already been created
                self.setup_figure()

    @property
    def plot_cumulative(self) -> bool:
        r"""If the cumulative (integrated) PSD or spectrum is plotted on
        a subplot.

        The cumulative PSD is given by

        .. math::
            \mathrm{RMS}_S(f)^2 = \int_{f_\mathrm{min}}^f\mathrm{d}f^\prime\,S(f^\prime)

        with :math:`\mathrm{RMS}_S(f)` the root-mean-square of
        :math:`S(f^\prime)` up to frequency :math:`f^\prime`.

        If :attr:`plot_amplitude` is true, plot the square root of this,
        i.e., :math:`\mathrm{RMS}_S(f)`.
        """
        return self._plot_cumulative

    @plot_cumulative.setter
    def plot_cumulative(self, val: bool):
        val = bool(val)
        if val != self._plot_cumulative:
            self._plot_cumulative = val
            self.update_line_attrs(['cumulative'], self.lines_to_draw, stale=True, hidden=not val)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_timetrace(self) -> bool:
        """If the timetrace data is plotted on a subplot.

        The absolute value is plotted if the time series is complex."""
        return self._plot_timetrace

    @plot_timetrace.setter
    def plot_timetrace(self, val: bool):
        val = bool(val)
        if val != self._plot_timetrace:
            self._plot_timetrace = val
            self.update_line_attrs(['time'], self.lines_to_draw, stale=True, hidden=not val)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_negative_frequencies(self) -> bool:
        """Plot the negative frequencies for a two-sided spectrum."""
        return self._plot_negative_frequencies

    @plot_negative_frequencies.setter
    def plot_negative_frequencies(self, val: bool):
        val = bool(val)
        if val != self._plot_negative_frequencies:
            self._plot_negative_frequencies = val
            self.update_line_attrs(['main', 'cumulative'], self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_absolute_frequencies(self) -> bool:
        """For a lock-ins, plot physical frequencies at the input.

        This means the displayed frequencies are shifted by the
        demodulation frequency, which must be present in the settings
        under the keyword 'freq'."""
        return self._plot_absolute_frequencies

    @plot_absolute_frequencies.setter
    def plot_absolute_frequencies(self, val: bool):
        val = bool(val)
        if val != self._plot_absolute_frequencies:
            self._plot_absolute_frequencies = val
            self.update_line_attrs(
                plots=['main', 'cumulative'],
                keys=[key for key in self.shown if 'freq' in self._data[key]['settings']],
                stale=True
            )
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_amplitude(self) -> bool:
        """If the amplitude spectral density is plotted instead of the
        power spectral density (ASD = sqrt(PSD)).

        Also applies to the cumulative spectrum, in which case that plot
        corresponds to the cumulative mean square instead of the root-
        mean-square (RMS)."""
        return self._plot_amplitude

    @plot_amplitude.setter
    def plot_amplitude(self, val: bool):
        val = bool(val)
        if val != self._plot_amplitude:
            self._plot_amplitude = val
            self.update_line_attrs(['main', 'cumulative'], self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_density(self) -> bool:
        """Plot the density or the spectrum."""
        return self._plot_density

    @plot_density.setter
    def plot_density(self, val: bool):
        val = bool(val)
        if val != self._plot_density:
            self._plot_density = val
            self.update_line_attrs(['main', 'cumulative'], self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_cumulative_normalized(self) -> bool:
        """If the cumulative spectrum is plotted normalized."""
        return self._plot_cumulative_normalized

    @plot_cumulative_normalized.setter
    def plot_cumulative_normalized(self, val: bool):
        val = bool(val)
        if val != self._plot_cumulative_normalized:
            self._plot_cumulative_normalized = val
            self.update_line_attrs(['cumulative'], self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_style(self) -> _styleT:
        """The matplotlib style used for plotting.

        See :attr:`matplotlib.style.available` for all available
        styles. Default is 'fast'.
        """
        return self._plot_style

    @plot_style.setter
    def plot_style(self, val: _styleT):
        if val != self._plot_style:
            try:
                with plt.style.context(val):
                    pass
            except OSError as err:
                warnings.warn(f'Ignoring style {val} due to the following error:\n{err}',
                              UserWarning, stacklevel=2)
                return

            self._plot_style = val
            self.destroy_axes()
            self.update_line_attrs(self.plots_to_draw, self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def plot_dB_scale(self) -> bool:
        """Plot data as dB relative to a reference spectrum.

        See also :attr:`reference_spectrum`."""
        return self._plot_dB_scale

    @plot_dB_scale.setter
    def plot_dB_scale(self, val: bool):
        val = bool(val)
        if val != self._plot_dB_scale:
            self._plot_dB_scale = val
            self.update_line_attrs(['main', 'cumulative'], self.lines_to_draw, stale=True)
            if self.is_fig_open():
                self.setup_figure()

    @property
    def reference_spectrum(self) -> Optional[tuple[int, str]]:
        """Spectrum taken as a reference for the dB scale.

        See also :attr:`plot_dB_scale`."""
        if self._reference_spectrum is None and self._data:
            return list(self._data)[0]
        return self._reference_spectrum

    @reference_spectrum.setter
    def reference_spectrum(self, val: tuple[int, str]):
        self._reference_spectrum = val

    @property
    def processed_unit(self) -> str:
        """The unit displayed for processed data."""
        return self._processed_unit

    @processed_unit.setter
    def processed_unit(self, val: str):
        val = str(val)
        if val != self._processed_unit:
            self._processed_unit = val
            if self.is_fig_open():
                self.setup_figure()

    @property
    def complex_data(self) -> bool:
        """Is there complex data resulting in negative frequencies in the FFT?"""
        if self._complex_data is not None:
            return self._complex_data

        complex_raw_data = any(np.iscomplexobj(d['timetrace_raw'])
                               for d in self._data.values()
                               if 'timetrace_raw' in d)
        complex_processed_data = any(np.iscomplexobj(d['timetrace_processed'])
                                     for d in self._data.values()
                                     if 'timetrace_processed' in d)
        return complex_raw_data or complex_processed_data

    @with_plot_context
    def plot_or_set_props(self, x, y, key, plot_type, line_type):
        d = self.lines[key][plot_type][line_type]
        if line := d['line']:
            line.set_data(x, y)
            line.set_color(self.line_props(key[0], d)['color'])
            line.set_alpha(self.line_props(key[0], d)['alpha'])
            line.set_zorder(self.line_props(key[0], d)['zorder'])
        else:
            line, = self.axes[plot_type][line_type].plot(x, y, **self.line_props(key[0], d))
        self.update_line_attrs([plot_type], [line_type], [key], stale=False, line=line)

    @with_plot_context
    def main_plot(self, key, line_type):
        x, y = self.get_freq_data(key, line_type, self.plot_dB_scale)
        self.plot_or_set_props(x, y, key, 'main', line_type)

    @with_plot_context
    def cumulative_plot(self, key, line_type):
        # y is the power irrespective of whether self.plot_amplitude is True or not.
        # This means that if the latter is True, this plot shows the cumulative RMS,
        # and if it's False the cumulative MS (mean square, variance).
        x, y = self.get_integrated_data(key, line_type, self.plot_dB_scale)
        self.plot_or_set_props(x, y, key, 'cumulative', line_type)

    @with_plot_context
    def time_plot(self, key, line_type):
        y = self._data[key][f'timetrace_{line_type}'][-1]
        if np.iscomplexobj(y):
            y = np.abs(y)
        x = np.arange(y.size) / self._data[key]['settings']['fs']
        self.plot_or_set_props(x, y, key, 'time', line_type)

    @with_plot_context
    def setup_figure(self):
        gs = gridspec.GridSpec(2 + self.plot_cumulative + self.plot_timetrace, 1, figure=self.fig,
                               **self.gridspec_kw)
        self.setup_main_axes(gs)
        self.setup_cumulative_axes(gs)
        self.setup_time_axes(gs)
        self.destroy_unused_axes()
        self.update_figure()

    @with_plot_context
    def setup_main_axes(self, gs: gridspec.GridSpec):
        if self.axes['main']['processed'] is None:
            self.axes['main']['processed'] = self.fig.add_subplot(gs[:2], **self.subplot_kw)
            self.axes['main']['processed'].grid(True)
        self.axes['main']['processed'].set_xscale('log')
        self.axes['main']['processed'].set_yscale('linear' if self.plot_dB_scale else 'log')
        # can change
        self.axes['main']['processed'].set_xlabel('$f$ (Hz)' if not self.plot_cumulative else '')
        self.axes['main']['processed'].set_ylabel(
            _ax_label(self.plot_amplitude, False, self.plot_dB_scale, self.reference_spectrum)
            + _ax_unit(self.plot_amplitude, self.plot_density, False,
                       self.plot_cumulative_normalized, self.plot_dB_scale, self.processed_unit)
        )
        self.axes['main']['processed'].xaxis.set_tick_params(which="both",
                                                             labelbottom=not self.plot_cumulative)
        if self.plot_raw:
            if self.axes['main']['raw'] is None:
                self.axes['main']['raw'] = self.axes['main']['processed'].twinx()
            self.axes['main']['raw'].set_yscale('linear' if self.plot_dB_scale else 'log')
            # can change
            self.axes['main']['raw'].set_ylabel(
                _ax_label(self.plot_amplitude, False, self.plot_dB_scale, self.reference_spectrum)
                + _ax_unit(self.plot_amplitude, self.plot_density, False,
                           self.plot_cumulative_normalized, self.plot_dB_scale, self.raw_unit)
            )
        self.set_subplotspec('main', gs[:2])

    @with_plot_context
    def setup_cumulative_axes(self, gs: gridspec.GridSpec):
        if self.plot_cumulative:
            if self.axes['cumulative']['processed'] is None:
                self.axes['cumulative']['processed'] = self.fig.add_subplot(
                    gs[2], sharex=self.axes['main']['processed'], **self.subplot_kw
                )
                self.axes['cumulative']['processed'].grid(True)
                self.axes['cumulative']['processed'].set_xlabel('$f$ (Hz)')
            self.axes['cumulative']['processed'].set_xscale('log')
            # can change
            self.axes['cumulative']['processed'].set_ylabel(
                _ax_label(self.plot_amplitude, True, self.plot_dB_scale, self.reference_spectrum)
                + _ax_unit(self.plot_amplitude, self.plot_density, True,
                           self.plot_cumulative_normalized, self.plot_dB_scale,
                           self.processed_unit)
            )
            if self.plot_raw:
                if self.axes['cumulative']['raw'] is None:
                    self.axes['cumulative']['raw'] = self.axes['cumulative']['processed'].twinx()
                # can change
                self.axes['cumulative']['raw'].set_ylabel(
                    _ax_label(self.plot_amplitude, True, self.plot_dB_scale,
                              self.reference_spectrum)
                    + _ax_unit(self.plot_amplitude, self.plot_density, True,
                               self.plot_cumulative_normalized, self.plot_dB_scale, self.raw_unit)
                )
            self.set_subplotspec('cumulative', gs[2])

    @with_plot_context
    def setup_time_axes(self, gs: gridspec.GridSpec):
        if self.plot_timetrace:
            if self.axes['time']['processed'] is None:
                self.axes['time']['processed'] = self.fig.add_subplot(gs[-1], **self.subplot_kw)
                self.axes['time']['processed'].grid(True)
                self.axes['time']['processed'].set_xlabel('$t$ (s)')
            # can change
            self.axes['time']['processed'].set_ylabel(f'Amplitude ({self.processed_unit})')
            if self.plot_raw:
                if self.axes['time']['raw'] is None:
                    self.axes['time']['raw'] = self.axes['time']['processed'].twinx()
                # can change
                self.axes['time']['raw'].set_ylabel(f'Amplitude ({self.raw_unit})')
            self.set_subplotspec('time', gs[-1])

    def destroy_axes(self,
                     plots: Iterable[str] = PLOT_TYPES,
                     lines: Iterable[str] = LINE_TYPES):
        self.destroy_lines(plots, lines)
        for plot in plots:
            for line in lines:
                try:
                    self.axes[plot][line].remove()
                    self.axes[plot][line] = None
                except (AttributeError, NotImplementedError):
                    # Ax None / Artist dead
                    continue

    def destroy_unused_axes(self):
        if not self.plot_raw:
            self.destroy_axes(lines=['raw'])
        self.destroy_axes(set(self.PLOT_TYPES).difference(self.plots_to_draw))

    def destroy_lines(self,
                      plots: Iterable[str] = PLOT_TYPES,
                      lines: Iterable[str] = LINE_TYPES,
                      keys: Optional[Iterable[_keyT]] = None):
        for key in keys or self.shown:
            for plot in plots:
                for line in lines:
                    try:
                        self.lines[key][plot][line]['line'].remove()
                        self.lines[key][plot][line]['line'] = None
                        self.lines[key][plot][line]['stale'] = None
                        self.lines[key][plot][line]['hidden'] = None
                    except AttributeError:
                        # Line None
                        continue

    @with_plot_context
    def update_figure(self):
        # Flush out all idle events, necessary for some reason in sequential mode
        self.fig.canvas.flush_events()

        # First set new axis scales and x-limits, then update the lines (since the cumulative
        # spectrum plot changes dynamically with the limits). Once all lines are drawn, update
        # y-limits
        self.set_xscales()
        self.set_xlims()
        self.update_lines()
        self.set_ylims()

        try:
            labels, handles = zip(*sorted(zip(self.shown,
                                              [val['main']['processed']['line']
                                               for val in self.lines.values()
                                               if val['main']['processed']['line'] is not None])))
            self._leg = self.ax[0].legend(handles=handles, labels=labels, **self.legend_kw)
        except ValueError:
            # Nothing to show or no data, do not draw the legend / remove it
            if self._leg is not None:
                self._leg.remove()

        if 'layout' not in self.figure_kw:
            try:
                self.fig.set_layout_engine('tight')
                self.fig.get_layout_engine().execute(self.fig)
            finally:
                self.fig.set_layout_engine('none')

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    @with_plot_context
    def update_lines(self):
        for key in self.shown:
            for plot in self.plots_to_draw:
                for line in self.lines_to_draw:
                    if self.lines[key][plot][line]['stale']:
                        getattr(self, f'{plot}_plot')(key, line)

    def add_new_line_entry(self, key: tuple[int, str]):
        self.lines[key] = dict.fromkeys(self.PLOT_TYPES)
        for plot in self.PLOT_TYPES:
            self.lines[key][plot] = dict.fromkeys(self.LINE_TYPES)
            for line in self.LINE_TYPES:
                self.lines[key][plot][line] = dict.fromkeys(['line', 'color', 'stale', 'hidden'])
            self.lines[key][plot]['processed']['zorder'] = 5
            self.lines[key][plot]['processed']['alpha'] = 1
            self.lines[key][plot]['raw']['zorder'] = 4
            self.lines[key][plot]['raw']['alpha'] = 0.5

    def set_subplotspec(self, plot: str, gs: gridspec.GridSpec):
        for line in self.lines_to_draw:
            self.axes[plot][line].set_subplotspec(gs)

    @with_plot_context
    def set_xlims(self):
        # Frequency-axis plots
        right = max((
            self._data[k]['settings']['f_max']
            + (self._data[k]['settings'].get('freq', 0)
               if self.plot_absolute_frequencies else 0)
            for k in self.shown
        ), default=None)
        if (
                not self.plot_negative_frequencies
                or self.axes['main']['processed'].get_xscale() == 'log'
        ):
            left = min((
                self._data[k]['settings']['f_min']
                + (self._data[k]['settings'].get('freq', 0)
                   if self.plot_absolute_frequencies else 0)
                for k in self.shown
            ), default=None)
        else:
            left = min((
                - self._data[k]['settings']['f_max']
                + (self._data[k]['settings'].get('freq', 0)
                   if self.plot_absolute_frequencies else 0)
                for k in self.shown
            ), default=None)

        with filter_warnings(action='ignore', category=UserWarning):
            # ignore warnings issued for empty plots with log scales
            self.axes['main']['processed'].set_xlim(left, right)

        # Time-axis plot
        # Need to call relim before autoscale in case we used set_data()
        # before, see :meth:`matplotlib.axes.Axes.autoscale_view`
        if self.plot_timetrace:
            self.axes['time']['processed'].relim(visible_only=True)
            self.axes['time']['processed'].autoscale(enable=True, axis='x', tight=True)

    @with_plot_context
    def set_ylims(self):
        if not self.shown:
            return

        margin = plt.rcParams['axes.ymargin']
        for plot in self.plots_to_draw:
            for line in self.lines_to_draw:
                top = -np.inf
                bottom = np.inf
                for key in self.shown:
                    left, right = self.axes[plot][line].get_xlim()
                    xdata = self.lines[key][plot][line]['line'].get_xdata()
                    ydata = self.lines[key][plot][line]['line'].get_ydata()[
                        (left <= xdata) & (xdata <= right)
                    ]
                    top = max(top, np.nanmax(ydata))
                    bottom = min(bottom, np.nanmin(ydata))
                # Transform to correct scale
                transform = self.axes[plot][line].transScale
                top, bottom = transform.transform([(1, top),
                                                   (1, bottom)])[:, 1]
                interval = top - bottom
                top += margin * interval
                bottom -= margin * interval
                # Transform back
                top, bottom = transform.inverted().transform([(1, top),
                                                              (1, bottom)])[:, 1]
                with filter_warnings(action='ignore', category=UserWarning):
                    # If bottom = top
                    self.axes[plot][line].set_ylim(bottom, top)

    @with_plot_context
    def set_xscales(self):
        if self.complex_data and self.plot_negative_frequencies:
            # If daq returns complex data, the spectrum will have negative freqs
            if self.axes['main']['processed'].get_xscale() == 'log':
                # matplotlib>=3.6 has asinh scale for log plots with negative values
                self.axes['main']['processed'].set_xscale(_asinh_scale_maybe())
                if self.plot_cumulative:
                    self.axes['cumulative']['processed'].set_xscale(_asinh_scale_maybe())
        else:
            if self.axes['main']['processed'].get_xscale() != 'log':
                self.axes['main']['processed'].set_xscale('log')
                if self.plot_cumulative:
                    self.axes['cumulative']['processed'].set_xscale('log')

    def update_line_attrs(self,
                          plots: Iterable[str] = PLOT_TYPES,
                          lines: Iterable[str] = LINE_TYPES,
                          keys: Optional[Iterable[_keyT]] = None,
                          **kwargs):
        for key in keys or self.shown:
            for plot in plots:
                for line in lines:
                    self.lines[key][plot][line].update(kwargs)

    def line_props(self, index: int, line_dct: dict) -> dict:
        props = {key: val[index % len(self.prop_cycle)]
                 for key, val in self.prop_cycle.by_key().items()}
        # Default values for raw/processed lines
        props.setdefault('zorder', line_dct['zorder'])
        props.setdefault('alpha', line_dct['alpha'])
        # Color can be overridden in show()
        if line_dct['color'] is not None:
            props['color'] = line_dct['color']
        return props

    def drop_lines(self, key: _keyT):
        del self.lines[key]

    def get_freq_data(self, key, line_type, dB) -> tuple[np.ndarray, np.ndarray]:
        y = np.mean(np.atleast_2d(self._data[key][f'S_{line_type}']), axis=0)
        x = self._data[key][f'f_{line_type}'].copy()
        if self.plot_absolute_frequencies:
            x += self._data[key]['settings'].get('freq', 0)

        window = self._data[key]['settings'].get(
            'window', 'hann' if self.uses_windowed_estimator else 'boxcar'
        )
        nperseg = self._data[key]['settings']['nperseg']
        fs = self._data[key]['settings']['fs']
        if isinstance(window, str) or isinstance(window, tuple):
            window = signal.get_window(window, nperseg)
        else:
            window = np.asarray(window)

        if not self.plot_density:
            y *= fs * (window ** 2).sum() / window.sum() ** 2
        if self.plot_amplitude:
            # If db, this correctly accounts for the factor two in the definition below
            y **= 0.5
        if dB:
            # It does not matter whether we plot the density or the spectrum because the factor
            # between them cancels out
            x0, y0 = self.get_freq_data(self.reference_spectrum, line_type, dB=False)
            y = self.to_dB(x0, y0, x, y, key)

        return x, y

    def get_integrated_data(self, key, line_type, dB=False):
        # Should not integrate over dB but do the conversion afterward
        x, y = self.get_freq_data(key, line_type, dB=False)
        if self.plot_amplitude:
            # Need to integrate over power always...
            y **= 2.0
        x_min, x_max = self.axes['cumulative'][line_type].get_xlim()
        mask = (x_min <= x) & (x <= x_max)
        x = x[..., mask]
        y = y[..., mask]
        y = integrate.cumulative_trapezoid(y, x, initial=0, axis=-1)
        if self.plot_amplitude:
            # and then convert back if desired.
            y **= 0.5
        if dB:
            x0, y0 = self.get_integrated_data(self.reference_spectrum, line_type, dB=False)
            y = self.to_dB(x0, y0, x, y, key)
            if self.plot_cumulative_normalized:
                warnings.warn('plot_cumulative_normalized does not make sense together with '
                              'plot_dB_scale. Ignoring.', UserWarning, stacklevel=3)
        elif self.plot_cumulative_normalized:
            y = (y - y.min()) / np.ptp(y)

        return x, y

    def to_dB(self, x0, y0, x, y, key):
        with np.errstate(divide='ignore', invalid='ignore'):
            try:
                y = 10 * np.log10(y / y0)
            except ValueError as error:
                raise RuntimeError(f'dB scale requested but data for key {key} does not have '
                                   'the same shape as reference data with key '
                                   f'{self.reference_spectrum}. Select a different reference '
                                   'using Spectrometer.set_reference_spectrum() or adapt your '
                                   'acquisition parameters') from error
            else:
                # infs are from zero-division, nans from 0/0. The latter occurs for the first point
                # in integrated spectra, so set manually to log(1)=0. Infs we mask with nans.
                y[np.isnan(y)] = 0
                y[np.isinf(y)] = np.nan

        assert np.allclose(x, x0)
        return y


def _ax_unit(amplitude: bool, density: bool, integrated: bool, cumulative_normalized: bool,
             dB: bool, unit: str) -> str:
    if integrated and cumulative_normalized:
        return ' (a.u.)'
    elif dB:
        return ' (dB)'
    elif not amplitude:
        unit = unit + '$^2$'

    labels = {
        # (amplitude, density, integrated)
        (False, False, False): f' ({unit})',
        (False, False, True): f' ({unit}' + r'$\mathrm{Hz}$)',
        (False, True, False): f' ({unit}' + r'$/\mathrm{Hz}$)',
        (False, True, True): f' ({unit})',
        (True, False, False): f' ({unit})',
        (True, False, True): f' ({unit}' + r'$\sqrt{\mathrm{Hz}}$)',
        (True, True, False): f' ({unit}' + r'$/\sqrt{\mathrm{Hz}}$)',
        (True, True, True): f' ({unit})',
    }
    return labels[(amplitude, density, integrated)]


def _ax_label(amplitude: bool, integrated: bool, dB: bool, reference: Union[_keyT, None]) -> str:
    labels = {
        (False, False, False): '$S(f)$',
        (False, True, False): r'$\sqrt{S(f)}$',
        (False, False, True): r'$\mathrm{RMS}_S(f)^2$',
        (False, True, True): r'$\mathrm{RMS}_S(f)$'
    }
    if dB:
        labels |= {
            (True, False, False): f'Pow. rel. to key {reference[0]}',
            (True, True, False): f'Amp. rel. to key {reference[0]}',
            (True, False, True): f'Int. pow. rel. to key {reference[0]}',
            (True, True, True): f'Int. amp. rel. to key {reference[0]}'
        }
    return labels[(dB, amplitude, integrated)]


def _asinh_scale_maybe() -> Literal['asinh', 'linear']:
    try:
        getattr(scale, 'AsinhScale')
    except AttributeError:
        return 'linear'
    else:
        return 'asinh'
