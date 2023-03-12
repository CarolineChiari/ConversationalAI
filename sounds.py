# Play a sound to indicate recording session is on or about to be stopped.
import simpleaudio as sa
import numpy as np

def play_sound():
    # set the frequency and duration
    frequency = 440
    duration = 0.1  # in seconds

    # create a waveform
    sample_rate = 44100
    amplitude = 16000

    waveform = np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)
    waveform = (waveform * amplitude).astype(np.int16)

    # create a simpleaudio object
    audio = sa.play_buffer(waveform, 1, 2, sample_rate)

    # wait for the waveform to finish playing
    audio.wait_done()