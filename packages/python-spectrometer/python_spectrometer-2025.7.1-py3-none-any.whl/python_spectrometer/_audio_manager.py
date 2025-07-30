""" This module contains methods for using auditory channels to interface to humans """
import os
import queue
import threading
import time
from typing import Literal, Union

import numpy as np
from scipy import signal

try:
    import pyaudio
except ImportError:
    pyaudio = None


def _waveform_playback_target(waveform_queue: queue.Queue, stop_flag: threading.Event, max_playbacks: Union[int, float], bitrate: int):
    """ This function will be started in a separate thread to feed the audio output with new data.
    """

    pyaudio_instance = pyaudio.PyAudio()

    try:
        stream = pyaudio_instance.open(format=pyaudio.paFloat32,
                                       channels=1,
                                       rate=bitrate,
                                       output=True)
    except OSError:
        if os.environ.get('GITLAB_CI', 'false').lower() == 'true':
            return pyaudio_instance.terminate()
        else:
            raise

    last_waveform = None
    repeats = 0

    # run the playback look until the stop flag is set
    try:
        while not stop_flag.is_set():

            # waiting for a sample
            while last_waveform is None and waveform_queue.empty() and not stop_flag.is_set():
                time.sleep(0.01)

            # getting the latest sample from the queue and resetting the playback counter
            while not waveform_queue.empty() and not stop_flag.is_set():
                last_waveform = waveform_queue.get()
                repeats = 0

            # exit the playback loop then the stop flag is set.
            if stop_flag.is_set(): break

            # playing back the last sample and increasing the counter
            # this plays the last sample on repeat up to a set number of repetitions
            if last_waveform is not None:
                stream.write(last_waveform)
                repeats += 1

            # if the counter surpasses the max_playbacks, remove the sample
            if repeats >= max_playbacks:
                last_waveform = None
    finally:
        # the stop_flag has been raised, thus thing will be closed.
        stream.close()
        pyaudio_instance.terminate()



class WaveformPlaybackManager:
    """ Manages a thread used to play back the recorded noise samples.
    This class has been written with the help of ChatGPT 4o.

    Parameter
    ---------
    max_playbacks : Union[int, float]
        How often one sample is to be replayed. If 1 is given, then the sample is played back only once. If 10 is given, then the sample is played back 10 times if no new waveform is acquired. if np.inf is given, then the sample is played back until the AudtoryManager.stop() is called. (default = 10)
    audio_amplitude_normalization : Union[Literal["single_max"], float], default "single_max"
        The factor with with which the waveform is divided by to
        normalize the waveform. This can be used to set the volume.
        The default "single_max" normalized each sample depending on
        only that sample, thus the volume might not carry significant
        information.

    """

    def __init__(self, max_playbacks: int = 10, amplitude_normalization: Union[Literal["single_max"], float] = "single_max"):

        if pyaudio is None:
            raise ValueError("Please install PyAudio to listen to noise.")

        self.max_playbacks = max_playbacks
        self.amplitude_normalization = amplitude_normalization

        self.waveform_queue = queue.Queue()
        self.stop_flag = threading.Event()
        self.playback_thread = None
        self._BITRATE = 44100

    def start(self):
        """Starts the thread. The thread then waits until a samples is given via the notify method.
        """

        while not self.waveform_queue.empty():
            self.waveform_queue.get()

        self.stop_flag.clear()

        self.playback_thread = threading.Thread(target=_waveform_playback_target, args=(self.waveform_queue, self.stop_flag, self.max_playbacks, self._BITRATE))
        self.playback_thread.start()

    def notify(self, waveform:np.ndarray, bitrate:int):
        """ Sends a waveform of a noise sample to the playback thread. The thread is started if the thread is not running.
        """

        # calculating the number of samples that the waveform should have to fit the target bit rate.
        num = int(np.floor(self._BITRATE/bitrate*len(waveform)))

        # normalize the waveform
        if self.amplitude_normalization == "single_max":
            waveform /= np.max(np.abs(waveform))
        elif isinstance(self.amplitude_normalization, float):
            waveform /= np.abs(self.amplitude_normalization)

        waveform -= np.mean(waveform)

        # sample data to match the BITRATE
        waveform = signal.resample(waveform, num)

        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.start()

        self.waveform_queue.put(waveform.flatten().astype("float32"))

    def stop(self):
        """ Stops the playback and the thread.
        """

        # notify the thread
        self.stop_flag.set()

        # wait until the thread has terminated
        if self.playback_thread is not None and self.playback_thread.is_alive():
            self.playback_thread.join()

    def __del__(self):
        self.stop()
