import numpy as np
from utils.convolution import manual_convolution
from utils.dft_utils import smart_dft_idft


# -------------------------------------------------------------
# 1. PARSE FILTER SPECIFICATION FILE
# -------------------------------------------------------------
def parse_specification_file(filepath):
    params = {}

    with open(filepath, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=")
                params[key.strip().lower()] = value.strip()

    filter_type = params["filtertype"].lower()
    FS = float(params["fs"])
    A = float(params["stopbandattenuation"])
    TB = float(params["transitionband"])

    if filter_type in ["low pass", "high pass"]:
        FC = float(params["fc"])
        return filter_type, FS, A, TB, FC, None
    else:
        f1 = float(params["f1"])
        f2 = float(params["f2"])
        return filter_type, FS, A, TB, f1, f2

# -------------------------------------------------------------
# 2. CHOOSE WINDOW FROM ATTENUATION
# -------------------------------------------------------------
def choose_window(A):
    if A <= 21:
        return "rectangular"
    elif A <= 44:
        return "hanning"
    elif A <= 53:
        return "hamming"
    else:
        return "blackman"


def generate_window(window_type, N):
    n = np.arange(N)
    if window_type == "rectangular":
        return np.ones(N)
    if window_type == "hanning":
        return 0.5 - 0.5 * np.cos(2 * np.pi * n / (N - 1))
    if window_type == "hamming":
        return 0.54 - 0.46 * np.cos(2 * np.pi * n / (N - 1))
    if window_type == "blackman":
        return 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) + 0.08 * np.cos(4 * np.pi * n / (N - 1))


# -------------------------------------------------------------
# 3. COMPUTE N FROM ATTENUATION & TRANSITION BAND
# -------------------------------------------------------------
def compute_filter_length(A, TB, FS):
    # Normalize transition band
    Δf = TB / FS

    if A <= 21:
        N = np.ceil(0.9 / Δf)
    elif A <= 44:
        N = np.ceil(3.1 / Δf)
    elif A <= 53:
        N = np.ceil(3.3 / Δf)
    else:
        N = np.ceil(5.5 / Δf)

    # MUST BE ODD
    if N % 2 == 0:
        N += 1

    return int(N)




# -------------------------------------------------------------
# 4. IDEAL IMPULSE RESPONSES
# -------------------------------------------------------------
def ideal_lowpass(fc, N):
    wc = 2 * np.pi * fc
    M = (N - 1) // 2
    n = np.arange(N) - M
    hd = np.zeros(N)
    for i, k in enumerate(n):
        if k == 0:
            hd[i] = wc / np.pi
        else:
            hd[i] = np.sin(wc * k) / (np.pi * k)
    return hd


def ideal_highpass(fc, N):
    lp = ideal_lowpass(fc, N)
    delta = np.zeros(N)
    delta[(N - 1)//2] = 1
    return delta - lp


def ideal_bandpass(f1, f2, N):
    return ideal_lowpass(f2, N) - ideal_lowpass(f1, N)


def ideal_bandstop(f1, f2, N):
    M = (N - 1) // 2

    # Ideal Band-Pass part
    bpf = ideal_lowpass(f2, N) - ideal_lowpass(f1, N)

    # Delta impulse
    delta = np.zeros(N)
    delta[M] = 1

    # Band-Stop = delta - bandpass
    return delta - bpf



# -------------------------------------------------------------
# 5. MAIN FILTER DESIGN FUNCTION
# -------------------------------------------------------------
def design_fir_from_spec(filepath):

    FilterType, FS, A, TB, f1, f2 = parse_specification_file(filepath)

    # Normalize cutoff by fs THEN adjust for half transition band
    if FilterType in ["low pass", "high pass"]:
        fc = (f1 / FS)
        fc = fc + (TB / (2*FS)) if FilterType == "low pass" else fc - (TB / (2*FS))
        
    elif FilterType == "band pass": 
        f1 = (f1 / FS) + (TB / (2*FS)) * -1
        f2 = (f2 / FS) + (TB / (2*FS))

    elif FilterType == "band stop":
        f1 = (f1 / FS) + (TB / (2*FS))
        f2 = (f2 / FS) - (TB / (2*FS))


    # Compute filter length
    N = compute_filter_length(A, TB, FS)

    # Select window
    window_type = choose_window(A)
    w = generate_window(window_type, N)

    # Compute hd(n)
    if FilterType == "low pass":
        hd = ideal_lowpass(fc, N)
    elif FilterType == "high pass":
        hd = ideal_highpass(fc, N)
    elif FilterType == "band pass":
        hd = ideal_bandpass(f1, f2, N)
    else:
        hd = ideal_bandstop(f1, f2, N)

    # Final filter h(n)
    h = hd * w

    n = np.arange(-(N//2), (N//2)+1)

    return n.tolist(), h.tolist(), N


# -------------------------------------------------------------
# 6. SAVE COEFFICIENTS LIKE THE TESTCASE FORMAT
# -------------------------------------------------------------
def save_coeffs_like_example(filename, n, h):
    with open(filename, "w") as f:
        f.write("0\n0\n")              # first two lines from testcase
        f.write(f"{len(h)}\n")        # N
        for i in range(len(n)):
            f.write(f"{n[i]} {h[i]}\n")


# -------------------------------------------------------------
# 7. APPLY FILTERING
# -------------------------------------------------------------
def filter_time_domain(indices, samples, h):
    samples = np.array(samples, dtype=float)
    h = np.array(h, dtype=float)

    # FULL convolution
    y = np.array(manual_convolution(samples, h))

    M = len(h) // 2

    # FULL convolution indices
    start_index = indices[0] - M
    new_indices = np.arange(start_index, start_index + len(y))

    return new_indices.tolist(), y.tolist()


def filter_freq_domain(indices, samples, h):
    x = np.array(samples, dtype=float)
    h = np.array(h, dtype=float)

    L = len(x) + len(h) - 1

    X = smart_dft_idft(np.pad(x, (0, L - len(x))), inverse=False)
    H = smart_dft_idft(np.pad(h, (0, L - len(h))), inverse=False)

    y = np.real(smart_dft_idft(X * H, inverse=True))

    M = len(h) // 2
    start_index = indices[0] - M
    new_indices = np.arange(start_index, start_index + len(y))

    return new_indices.tolist(), y.tolist()
