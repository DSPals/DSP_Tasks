import os
import numpy as np

from utils.file_utils import read_signal

def normalized_correlation(x, h):
    x = np.array(x, dtype=float)
    h = np.array(h, dtype=float)
    N = len(x)
    
    denom = np.sqrt(np.sum(x**2) * np.sum(h**2))
    if denom == 0:
        return list(range(N)), [0.0]*N

    corr_values = []
    for j in range(N):
        s = sum(x[n] * h[(n + j) % N] for n in range(N))
        corr_values.append(s / denom)
    
    indices = list(range(N))
    return indices, corr_values

def Compare_Signals(file_name,Your_indices,Your_samples):      
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    print("Current Output Test file is: ")
    print(file_name)
    print("\n")
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Shift_Fold_Signal Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Shift_Fold_Signal Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Correlation Test case failed, your signal have different values from the expected one") 
            return
    print("Correlation Test case passed successfully")

def read_signal_values_only(file_path):
    values = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                values.append(float(line))
    return np.array(values, dtype=float)

def read_uploaded_values_only(uploaded_file):
    values = []
    for line in uploaded_file:
        line = line.decode("utf-8").strip()
        if line:
            values.append(float(line))
    return np.array(values, dtype=float)

def normalize_signal(x):
    return (x - np.mean(x)) / (np.std(x) + 1e-8)

def classify_signal_avg_max(test_signal, class1_signals, class2_signals):

    def avg_max_corr(test, signals):
        max_corrs = []
        for s in signals:
            L = min(len(test), len(s))
            test_n = normalize_signal(test[:L])
            s_n = normalize_signal(s[:L])
            _, corr = normalized_correlation(test_n, s_n)

            max_corrs.append(np.max(np.abs(corr)))
        return np.mean(max_corrs)

    c1_avg = avg_max_corr(test_signal, class1_signals)
    c2_avg = avg_max_corr(test_signal, class2_signals)

    label = "Class 1 (Down Movement)" if c1_avg > c2_avg else "Class 2 (Up Movement)"
    return label, c1_avg, c2_avg

def load_signals_from_folder(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    signals = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(".txt"):
            full_path = os.path.join(folder_path, file)
            values = read_signal_values_only(full_path)
            signals.append(values)

    return signals

