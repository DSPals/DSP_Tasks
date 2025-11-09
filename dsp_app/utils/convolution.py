import numpy as np

def manual_convolution(x, h):
    x = np.array(x, dtype=float)
    h = np.array(h, dtype=float)
    y_length = len(x) + len(h) - 1
    y = np.zeros(y_length)
    for n in range(y_length):
        for k in range(len(x)):
            if 0 <= n - k < len(h):
                y[n] += x[k] * h[n - k]
    return y.tolist()

def moving_average(x, window_size):
    window_size = min(window_size, len(x))
    x = np.array(x, dtype=float)
    y = []
    for n in range(len(x) - window_size + 1):
        window = x[n : n + window_size]
        y.append(np.mean(window))
    return y

def first_derivative(x):
    x = np.array(x, dtype=float)
    return [x[n+1] - x[n] for n in range(len(x) - 1)]

def second_derivative(x):
    x = np.array(x, dtype=float)
    return [x[n+2] - 2*x[n+1] + x[n] for n in range(len(x) - 2)]

