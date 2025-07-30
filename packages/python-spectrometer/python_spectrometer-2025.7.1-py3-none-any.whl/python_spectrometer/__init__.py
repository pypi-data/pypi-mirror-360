"""This module provides the :class:`~.Spectrometer` class for
spectrum estimation using general-purpose acquisition hardware. The
class manages the acquisition, processing, as well as displaying of
acquired data.

An object of the :class:`~.Spectrometer` class is instantiated with an
instance of the :class:`~daq.core.DAQ` class which implements thin
wrappers around hardware drivers in :mod:`.daq` by means of its
:meth:`~daq.core.DAQ.setup` and :meth:`~daq.core.DAQ.acquire` methods.
Conceptually, :meth:`~daq.core.DAQ.setup` should configure the hardware
for data acquisition given a dictionary of settings, while
:meth:`~daq.core.DAQ.acquire()` should execute said acquisition and
yield an array of data when iterated. Furthermore, a custom estimator
for the power spectral density can be supplied, which could for instance
perform some processing of the Fourier-transformed data before computing
the spectrum using the conventional Welch's method, or use some other
method of spectral estimation.

To give a better idea of what these functions should do without delving
into the source code, we outline how to implement them for the example
of a vibration measurement here. Assume the measurement device outputs
a voltage that is proportional to the acceleration, and we would like
to obtain the displacement spectrum::

    from qutil.signal_processing.real_space import welch
    from python_spectrometer.daq.base import DAQ

    def psd_estimator(taccel, **settings):
        '''PSD estimator for displacement profile from acceleration.'''
        def accel_to_displ(a, f, **settings):
            # Integration in Fourier space corresponds to division by ω
            return a/(2*np.pi*f)**2
        return welch(taccel, fourier_procfn=accel_to_displ), f

    class MyDAQ(DAQ):
        # daq is the actual device driver
        daq: object

        def setup(self, **settings):
            # Configure the hardware through some driver representing
            # the device by the daq object.
            daq.setup(...)
            # We may modify settings here, for instance to account for
            # hardware constraints.
            return settings

        def acquire(self, **settings):
            for _ in settings.get('n_avg', 1):
                yield daq.measure()  # yields ndarray with data
            return metadata  # optionally returns metadata

We can then instantiate a :class:`~core.Spectrometer` object like so::

    from python_spectrometer import Spectrometer

    daq = ...
    spect = Spectrometer(MyDAQ(daq), psd_estimator)

Spectra can then be acquired using the :meth:`~.Spectrometer.take`
method, which takes as arguments a comment to identify the spectrum by
as well as keyword-argument pairs of settings that are passed through
to :meth:`~daq.core.DAQ.setup`, :meth:`~daq.core.DAQ.acquire`, and
:func:`psd_estimator`::

    settings = {'f_max': 1234.5}
    spect.take('a comment', n_avg=5, **settings)

For the default PSD estimator
(:func:`qutil:qutil.signal_processing.real_space.welch`), a dictionary
subclass exists, :class:`daq.settings.DAQSettings`, which manages the
interdependencies of parameters for data acquisition. For example,
:attr:`~.daq.settings.DAQSettings.f_max` cannot be larger than half the
sampling rate :attr:`~.daq.settings.DAQSettings.fs` due to Nyquist's
theorem. See the class docstring for those special parameters.

Spectra can be hidden from the current display and shown again::

    spect.hide(0)
    spect.show('a comment')  # same as spect.show(0)

A run can also be serialized to disk and recalled at a later point::

    spect.serialize_to_disk('./foo')
    spect_loaded = Spectrometer.recall_from_disk('./foo')
    spect_loaded.print_keys()
    (0, 'a comment')
    spect_loaded.print_settings('a comment')
    Settings for key (0, 'a'):
    {...}

Finally, plot options can be changed dynamically at runtime::

    spect.plot_raw = True  # Updates the figure accordingly
    spect.plot_timetrace = False

Examples
--------

Example from :func:`scipy.signal.welch`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this short demonstration, we reproduce the example from
:func:`scipy:scipy.signal.welch`. To this end, we write a custom
``DAQ`` class that generates a noisy sine signal.

>>> import tempfile
>>> import numpy as np
>>> from python_spectrometer import Spectrometer
>>> from python_spectrometer.daq.base import DAQ
>>> class MyDAQ(DAQ):
...    rng = np.random.default_rng(1234)
...
...    def acquire(self, *, n_avg, fs, n_pts, amp=2*np.sqrt(2),
...                freq=1234.0, **settings):
...        noise_power = 0.001 * fs / 2
...        time = np.arange(n_pts) / fs
...        x = amp*np.sin(2*np.pi*freq*time)
...        for i in range(n_avg):
...            yield x + self.rng.normal(scale=np.sqrt(noise_power),
...                                      size=time.shape)
>>> spect = Spectrometer(MyDAQ(), savepath=tempfile.mkdtemp(),
...                      plot_cumulative=True, plot_amplitude=False,
...                      threaded_acquisition=False)
>>> spect.take('2 Vrms', fs=10e3, n_pts=1e5, nperseg=1024,
...            amp=2*np.sqrt(2))

Averaging the PSD yields the noise power on the signal.

>>> float(np.mean(spect[0]['S_processed'][0][256:]))
0.0009997881856675976

Computing the power spectrum instead yields an estimate for the RMS
of the peak. The 'flattop' window seems to give a more accurate result.

>>> spect.plot_density = False
>>> spect.plot_amplitude = True
>>> spect.reprocess_data(0, window='flattop')
>>> # Need to get from plot since internal data is unchanged
>>> data = spect.ax[0].lines[0].get_ydata()
>>> float(data.max())
2.009491183836163

Finally, we can also plot data in dB relative to a given dataset.

>>> spect.take('4 Vrms', fs=10e3, n_pts=1e5, nperseg=1024,
...            amp=4*np.sqrt(2), window='flattop')
>>> spect.plot_dB_scale = True
>>> spect.set_reference_spectrum(0)
>>> data = spect.ax[0].lines[1].get_ydata()
>>> float(data.max())  # Factor two in amplitude is approx 3 dB
3.0284739712568682

Analyzing filter behavior
^^^^^^^^^^^^^^^^^^^^^^^^^
:mod:`qutil:qutil.signal_processing.real_space` and
:mod:`qutil:qutil.signal_processing.fourier_space` define filters that
work in the time- and frequency-domain, respectively. We can visualize
the filter properties using the spectrometer:

>>> from tempfile import mkdtemp
>>> import qutil.signal_processing as sp
>>> from qutil.functools import partial
>>> from python_spectrometer import daq, Spectrometer

>>> def compare_filters(typ: str, order: int):
...     spect = Spectrometer(daq.QoptColoredNoise(), savepath=mkdtemp(),
...                          plot_dB_scale=True, plot_density=False,
...                          threaded_acquisition=False)
...     spect.take('Baseline', n_seg=10, fs=1e4, df=0.1)
...     spect.procfn = getattr(sp.real_space, f'{typ}_filter')
...     spect.take(f'Real space {order}. order {typ} filter',
...                n_seg=10, f_max=1e2, fs=1e4, df=0.1, order=order)
...     spect.procfn = sp.real_space.Id
...     spect.psd_estimator = partial(
...         sp.real_space.welch,
...         fourier_procfn=getattr(sp.fourier_space, f'{typ}_filter')
...     )
...     spect.take(f'Fourier space {order}. order {typ} filter',
...                n_seg=10, f_max=1e2, fs=1e4, df=0.1, order=order)

RC and Butterworth first order filters are the same (up to real-space
implementation):

>>> compare_filters('RC', 1)
>>> compare_filters('butter', 1)

For higher orders, they differ:

>>> compare_filters('RC', 5)
>>> compare_filters('butter', 5)


See the documentation of :class:`~core.Spectrometer` and its methods
for more information.
"""
__version__ = '2025.7.1'

from . import daq
from .core import Spectrometer
