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

def plot_signal(indices, values, title="Signal", mode="Discrete", sample = 0):
    fig, ax = plt.subplots()

    # ---- First signal ----
    if mode == "Continuous":
        ax.plot(indices, values, label=title, color="b")
    elif mode == "Discrete":
        ax.stem(indices, values, linefmt="b-", markerfmt="bo", basefmt="k-", label=title)
    elif mode == "Discrete + Continuous":
        ax.plot(indices, values, color="b", alpha=0.6, label=f"{title} (Continuous)")
        ax.stem(indices, values, linefmt="g-", markerfmt="go", basefmt="k-", label=f"{title} (Discrete)")

    # ---- Automatic axis labels ----
    if mode == "Continuous":
        ax.set_xlabel("t (seconds)")
        ax.set_ylabel("x[t]")
    elif mode == "Discrete":
        ax.set_xlabel("n (samples)")
        ax.set_ylabel("x[n]")
    elif mode == "Discrete + Continuous":
        ax.set_xlabel("t , n (time or sample index)")
        ax.set_ylabel("x[t], x[n]")

    if sample == 1:
        ax.set_xlabel("n (samples)")
        ax.set_ylabel("x[n]")
    

    ax.set_title(title)
    ax.grid(True, which="both")
    ax.legend()
    st.pyplot(fig)


def plot_multiple_signals(signals, mode="Discrete"):
    
    fig, ax = plt.subplots()

    colors = plt.cm.tab10(np.linspace(0, 1, len(signals)))
    markers = ["o", "s", "v", "^", "D", "x", "+", "*", "p", "h"]

    for i, sig in enumerate(signals):
        # Handle optional label
        if len(sig) == 3:
            indices, values, label = sig
        else:
            indices, values = sig
            label = f"Signal {i+1}"

        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]

        if mode == "Continuous":
            ax.plot(indices, values, label=label, color=color)
        elif mode == "Discrete":
            markerline, stemlines, baseline = ax.stem(indices, values, basefmt="k-", label=label)
            plt.setp(markerline, color=color, marker=marker)
            plt.setp(stemlines, color=color)
        elif mode == "Discrete + Continuous":
            ax.plot(indices, values, color=color, alpha=0.6, label=f"{label} (Continuous)")
            markerline, stemlines, baseline = ax.stem(indices, values, basefmt="k-", label=f"{label} (Discrete)")
            plt.setp(markerline, color=color, marker=marker)
            plt.setp(stemlines, color=color)

    # Axis labels
    if mode == "Continuous":
        ax.set_xlabel("t (seconds)")
        ax.set_ylabel("x[t]")
    elif mode == "Discrete":
        ax.set_xlabel("n (samples)")
        ax.set_ylabel("x[n]")
    else:
        ax.set_xlabel("t / n (time or sample index)")
        ax.set_ylabel("x[t], x[n]")

    ax.set_title("All Signals Comparison")
    ax.grid(True, which="both")
    ax.legend()
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
    return indices - k, values

def fold_signal(signal):
    indices, values = signal
    folded_indices = -indices
    sorted_order = np.argsort(folded_indices)
    return folded_indices[sorted_order], values[sorted_order]


def generate_analog_signal(wave_type, amplitude, phase, analog_freq, duration):
    
    analog_freq = float(analog_freq)
    duration = float(duration)

    t = np.linspace(0, duration, 5000)
    if wave_type == "Sine Wave":
        x = amplitude * np.sin(2 * np.pi * analog_freq * t + phase)
    else:
        x = amplitude * np.cos(2 * np.pi * analog_freq * t + phase)
    return t, x


def generate_discrete_signal(wave_type, amplitude, phase, analog_freq, sampling_freq, duration):
    analog_freq = float(analog_freq)
    sampling_freq = float(sampling_freq)
    duration = float(duration)
    
    # Generate discrete-time sample indices
    n = np.arange(0, int(duration * sampling_freq))
    t_n = n / sampling_freq 
    
    omega = 2 * np.pi * analog_freq / sampling_freq  
    
    if wave_type == "Sine Wave":
        x = amplitude * np.sin(omega * n + phase)
    else:
        x = amplitude * np.cos(omega * n + phase)

    return t_n, x  



# ==========================
# Test Functions 
# ========================== 

#!/usr/bin/env python
# coding: utf-8

def ReadSignalFile(file_name):
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
    return expected_indices,expected_samples

def AddSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name=r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\add.txt"
    expected_indices,expected_samples=ReadSignalFile(file_name)          
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Addition Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Addition Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Addition Test case failed, your signal have different values from the expected one") 
            return
    print("Addition Test case passed successfully")

def SubSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name=r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\subtract.txt"
        
    expected_indices,expected_samples=ReadSignalFile(file_name)   
    
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Subtraction Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Subtraction Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Subtraction Test case failed, your signal have different values from the expected one") 
            return
    print("Subtraction Test case passed successfully")
    
def MultiplySignalByConst(User_Const,Your_indices,Your_samples):
    if(User_Const==5):
        file_name=r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\mul5.txt" 
        
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Multiply by "+str(User_Const)+ " Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different values from the expected one") 
            return
    print("Multiply by "+str(User_Const)+" Test case passed successfully")

def ShiftSignalByConst(Shift_value,Your_indices,Your_samples):
    if(Shift_value==3):  #x(n+k)
        file_name=r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\advance3.txt" 
    elif(Shift_value==-3): #x(n-k)
        file_name=r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\delay3.txt"
        
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Shift by "+str(Shift_value)+" Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Shift by "+str(Shift_value)+" Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Shift by "+str(Shift_value)+" Test case failed, your signal have different values from the expected one") 
            return
    print("Shift by "+str(Shift_value)+" Test case passed successfully")

def Folding(Your_indices,Your_samples):
    file_name = r"D:\Downloads\Task 1 testcases and testing functions\Task 1 testcases and testing functions\folding.txt"
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Folding Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Folding Test case failed, your signal have different indicies from the expected one") 
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Folding Test case failed, your signal have different values from the expected one") 
            return
    print("Folding Test case passed successfully")

# ==========================
# GUI Functions 
# ========================== 

# use command py -m streamlit run d:\DSP_Tasks\DSP.py to run project

st.title("DSP Signal Processor")

menu = st.sidebar.radio("Main Menu", ["Signal Operations", "Signal Generation"])

display_mode = st.sidebar.selectbox("Display Mode", ["Discrete", "Continuous", "Discrete + Continuous"])

# File uploader
if menu == "Signal Operations":
    uploaded_files = st.file_uploader("Upload signal files", type=["txt"], accept_multiple_files=True)

    signals = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            indices, values = read_signal(uploaded_file)
            signals.append((indices, values))
            st.write(f"Loaded `{uploaded_file.name}` with {len(values)} samples")
            plot_signal(indices, values, title=f"{uploaded_file.name}", mode=display_mode)

    if signals:
        option = st.selectbox(
            "Choose Operation",
            [
                "Add Signals",
                "Multiply Signal by Constant",
                "Subtract Signals",
                "Delay/Advance",
                "Fold/Reverse",
                "Two Signals at the Same Time"
            ],
        )

        if option == "Add Signals" and len(signals) > 1:
            indices, result = add_signals(signals)
            plot_signal(indices, result, "Added Signal", mode=display_mode)
            download_signal(indices, result, "Download Added Signal", "added_signal.txt")
            AddSignalSamplesAreEqual("Signal1.txt", "Signal2.txt",indices,result) 

        elif option == "Multiply Signal by Constant":
            k = st.number_input("Enter constant (k):", value=2.0)
            indices, result = multiply_signal(signals[0], k)
            plot_signal(indices, result, f"Signal * {k}", mode=display_mode)
            download_signal(indices, result, f"Download Signal * {k}", f"signal_times_{k}.txt")
            MultiplySignalByConst(5,indices, result)

        elif option == "Subtract Signals" and len(signals) > 1:
            indices, result = subtract_signals(signals)
            plot_signal(indices, result, "Subtracted Signal", mode=display_mode)
            download_signal(indices, result, "Download Subtracted Signal", "subtracted_signal.txt")
            SubSignalSamplesAreEqual("Signal1.txt", "Signal2.txt",indices,result) 

        elif option == "Delay/Advance":
            k = st.number_input("Enter shift value (k):", value=-3)
            indices, result = shift_signal(signals[0], k)
            plot_signal(indices, result, f"Signal shifted by {k}", mode=display_mode)
            download_signal(indices, result, "Download Shifted Signal", f"signal_shifted_{k}.txt")
            ShiftSignalByConst(k,indices,result)  


        elif option == "Fold/Reverse":
            indices, result = fold_signal(signals[0])
            plot_signal(indices, result, "Folded Signal", mode=display_mode)
            download_signal(indices, result, "Download Folded Signal", "folded_signal.txt")
            Folding(indices,result)  


        elif option == "Signals at the Same Time" and len(signals) >= 2:
                labeled_signals = [(indices, values, uploaded_files[i].name if i < len(uploaded_files) else f"Signal {i+1}")
                                   for i, (indices, values) in enumerate(signals)]
                plot_multiple_signals(labeled_signals, mode=display_mode)
            
elif menu == "Signal Generation":     
    st.header("Signal Generation")

    wave_type = st.radio(
        "Select Wave Type",
        ["Sine Wave", "Cosine Wave"],
        horizontal=True
    )

    st.markdown("### Configure Your Signal Parameters")

    col1, col2 = st.columns(2)
    with col1:
        amplitude = st.number_input("Amplitude (A)", value=1.0, step=0.1, min_value=0.0)
        phase = st.number_input("Phase Shift (θ) [in radians]", value=0.0, step=0.1)
    with col2:
        analog_freq = st.number_input("Analog Frequency (Hz)", value=1.0, step=0.1, min_value=0.0)
        sampling_freq = st.number_input("Sampling Frequency (Hz)", value=10.0, step=0.1, min_value=0.0)

    st.markdown("---")
    col3, col4 = st.columns([1, 2])
    with col3:
        duration = st.number_input("Signal Duration (seconds)", value=1.0, step=0.1, min_value=0.1)
    with col4:
        st.empty()

    # Check Nyquist theorem
    if sampling_freq < 2 * analog_freq:
        st.error(
            f"❌ Sampling frequency must be at least **2 × Analog Frequency** "
            f"to satisfy the Nyquist theorem.\n\n"
            f"Currently: 2 × {analog_freq} = {2*analog_freq}, but Sampling = {sampling_freq}"
        )
        generate_button = st.button("Generate Signal", disabled=True)
    else:
        st.success("✅ Parameters satisfy the Nyquist theorem. You can generate the signal!")
        generate_button = st.button("Generate Signal")

    st.markdown("---")

    st.subheader("Signal Preview")
    if generate_button:
        st.info(f"Generating {wave_type.lower()} with A={amplitude}, θ={phase}, f={analog_freq}, fs={sampling_freq}, duration={duration}")
        t, analog_signal = generate_analog_signal(wave_type, amplitude, phase, analog_freq, duration)
        plot_signal(t, analog_signal, f"Analog {wave_type} (Continuous)", mode="Continuous")

        n, sampled_signal = generate_discrete_signal(wave_type, amplitude, phase, analog_freq, sampling_freq, duration)
        plot_signal(n, sampled_signal, f"Sampled {wave_type} (Discrete)", mode=display_mode,sample=1)
    else:
        st.write("Adjust parameters above and ensure Nyquist condition is satisfied to enable generation.")


















