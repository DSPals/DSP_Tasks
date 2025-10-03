import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# ==========================
# Utility Function 
# ========================== 

def read_signal(file):
    """Read a signal from a txt file (works for both uploaded file and path)."""
    if hasattr(file, "read"):  
        content = file.read().decode("utf-8").strip().split("\n")
    else: 
        with open(file, "r") as f:
            content = f.read().strip().split("\n")

    # clean lines
    content = [line.strip() for line in content if line.strip()]

    # detect where data starts (find first line with 2 numbers)
    start_idx = None
    for i, line in enumerate(content):
        if len(line.split()) == 2:
            start_idx = i
            break
        
    if start_idx is None:
        raise ValueError("No valid signal data found in file.")

    data = [list(map(int, line.split())) for line in content[start_idx:]]
    indices, values = zip(*data)
    return np.array(indices), np.array(values)

def plot_signal(indices, values, title="Signal"):
    fig, ax = plt.subplots()
    ax.stem(indices, values)  
    ax.set_title(title)
    ax.set_xlabel("n")
    ax.set_ylabel("x[n]")
    ax.grid(True, which="both")
    st.pyplot(fig)

def download_signal(indices, values, label="Download Result", default_name="output.txt"):
    buffer = io.StringIO()
    buffer.write(f"{len(values)}\n")
    for i, v in zip(indices, values):
        buffer.write(f"{i} {v}\n")
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=default_name,
        mime="text/plain"
    )

# ==========================
# Main Functions 
# ========================== 

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
    # take the first signal as is
    result = signals[0]
    # for the rest: multiply by -1 and add
    for sig in signals[1:]:
        neg_sig = multiply_signal(sig, -1)
        result = add_signals([result, neg_sig])
    return result


def shift_signal(signal, k):
    indices, values = signal
    return indices + k, values

def fold_signal(signal):
    indices, values = signal
    folded_indices = -indices
    sorted_order = np.argsort(folded_indices)
    return folded_indices[sorted_order], values[sorted_order]



# ==========================
# GUI Functions 
# ========================== 

# use command py -m streamlit run d:\DSP_Tasks\DSP.py to run project

st.title("DSP Signal Processor")

# File uploader
uploaded_files = st.file_uploader("Upload signal files", type=["txt"], accept_multiple_files=True)

signals = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        indices, values = read_signal(uploaded_file)
        signals.append((indices, values))
        st.write(f"Loaded `{uploaded_file.name}` with {len(values)} samples")
        plot_signal(indices, values, title=f"{uploaded_file.name}")

if signals:
    option = st.selectbox(
        "Choose Operation",
        [
            "Add Signals",
            "Multiply Signal by Constant",
            "Subtract Signals",
            "Delay/Advance",
            "Fold/Reverse",
        ],
    )

    if option == "Add Signals" and len(signals) > 1:
        indices, result = add_signals(signals)
        plot_signal(indices, result, "Added Signal")
        download_signal(indices, result, "Download Added Signal", "added_signal.txt")

    elif option == "Multiply Signal by Constant":
        k = st.number_input("Enter constant (k):", value=2)
        indices, result = multiply_signal(signals[0], k)
        plot_signal(indices, result, f"Signal * {k}")
        download_signal(indices, result, f"Download Signal * {k}", f"signal_times_{k}.txt")

    
    elif option == "Subtract Signals" and len(signals) > 1:
        indices, result = subtract_signals(signals)
        plot_signal(indices, result, "subtracted Signal")
        download_signal(indices, result, "Download Subtracted Signal", "subtracted_signal.txt")

    elif option == "Delay/Advance": 
        k = st.number_input("Enter constant (k):", value=0)
        indices, result = shift_signal(signals[0], k)
        plot_signal(indices, result, f"Signal shifted by {k}")
        download_signal(indices, result, f"Download Shifted Signal", f"signal_shifted_{k}.txt")

    elif option == "Fold/Reverse":
        indices, result = fold_signal(signals[0])
        plot_signal(indices, result, "Folded Signal")
        download_signal(indices, result, "Download Folded Signal", "folded_signal.txt")

    
