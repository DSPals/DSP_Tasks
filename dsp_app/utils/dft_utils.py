import numpy as np

def smart_dft_idft(x, inverse: bool = False):
    
    x = np.array(x, dtype=complex)

    N = x.shape[0]
    if N == 0:
        return np.array([], dtype=np.complex128)

    k = np.arange(N)
    n = k.reshape((N, 1))  

    if not inverse:
        # DFT
        exponent = -2j * np.pi * n * k / N
        W = np.exp(exponent)
        X = W @ x
        return X
    else:
        # IDFT
        exponent = 2j * np.pi * n * k / N
        W = np.exp(exponent)
        x_rec = (W @ x) / N
        return x_rec


def compute_amplitude_phase(X, unwrap_phase: bool = False):
    
    amp = np.abs(X)
    ph = np.angle(X)
    if unwrap_phase:
        ph = np.unwrap(ph)
    return amp, ph
