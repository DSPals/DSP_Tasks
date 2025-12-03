import numpy as np

def fft_manual(x):
    
    x = np.asarray(x, dtype=complex)
    N = x.shape[0]

    # Base case: length 1
    if N == 1:
        return x

    # Check power of 2
    if N % 2 != 0:
        raise ValueError(
            f"FFT requires N to be power of 2. Received length={N}. "
        )

    # Recursive FFT
    X_even = fft_manual(x[0::2])
    X_odd  = fft_manual(x[1::2])

    # Compute twiddle factors
    factor = np.exp(-2j * np.pi * np.arange(N) / N)

    # Combine
    return np.concatenate([
        X_even + factor[:N//2] * X_odd,
        X_even + factor[N//2:] * X_odd
    ])


def ifft_manual(X):
   
    X = np.asarray(X, dtype=complex)
    N = X.shape[0]

    # IFFT using FFT formula
    return np.conjugate(fft_manual(np.conjugate(X))) / N
