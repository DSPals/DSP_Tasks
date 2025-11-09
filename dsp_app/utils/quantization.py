import numpy as np

def quantize_signal(signal, num_levels=None, num_bits=None):
    indices, values = signal
    if num_bits is not None:
        num_levels = 2 ** int(num_bits)
    elif num_levels is None:
        raise ValueError("Either num_levels or num_bits must be provided")

    v_min, v_max = np.min(values), np.max(values)
    boundaries = np.linspace(v_min, v_max, num_levels + 1)
    q_levels = (boundaries[:-1] + boundaries[1:]) / 2

    quantized_values = []
    encoded_values = []
    interval_indices = []
    sampled_error = []

    for v in values:
        idx = np.clip(np.digitize(v, boundaries) - 1, 0, num_levels - 1)
        interval_indices.append(idx + 1)
        quantized_values.append(q_levels[idx])
        encoded_values.append(format(idx, f"0{int(np.log2(num_levels))}b"))
        sampled_error.append(q_levels[idx] - v)

    return interval_indices, encoded_values, quantized_values, sampled_error
