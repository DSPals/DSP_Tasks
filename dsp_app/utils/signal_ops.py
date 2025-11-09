import numpy as np

def add_signals(signals):
    result_dict = {}
    for indices, values in signals:
        for i, n in enumerate(indices):
            result_dict[n] = result_dict.get(n, 0) + values[i]
    indices = np.array(sorted(result_dict.keys()))
    values = np.array([result_dict[n] for n in indices])
    return indices, values

def multiply_signal(signal, k):
    indices, values = signal
    return indices, values * k

def subtract_signals(signals):
    result = signals[0]
    for sig in signals[1:]:
        neg_sig = multiply_signal(sig, -1)
        result = add_signals([result, neg_sig])
    return result

def shift_signal(signal, k):
    indices, values = signal
    return indices - k, values

def fold_signal(signal):
    indices, values = signal
    folded_indices = -indices
    sorted_order = np.argsort(folded_indices)
    return folded_indices[sorted_order], values[sorted_order]
