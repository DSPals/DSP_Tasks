import numpy as np

def generate_analog_signal(wave_type, amplitude, phase, analog_freq, duration):
    t = np.linspace(0, duration, 5000)
    if wave_type == "Sine Wave":
        x = amplitude * np.sin(2 * np.pi * analog_freq * t + phase)
    else:
        x = amplitude * np.cos(2 * np.pi * analog_freq * t + phase)
    return t, x

def generate_discrete_signal(wave_type, amplitude, phase, analog_freq, sampling_freq, duration):
    n = np.arange(0, int(duration * sampling_freq))
    omega = 2 * np.pi * analog_freq / sampling_freq
    if wave_type == "Sine Wave":
        x = amplitude * np.sin(omega * n + phase)
    else:
        x = amplitude * np.cos(omega * n + phase)
    return n, x
