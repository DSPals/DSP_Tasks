import streamlit as st
import numpy as np
import os
from utils.plot_utils import plot_signal
from utils.file_utils import read_signal
from utils.correlation_utils import *

def corr_tab(display_mode):

    st.header("Signal Analysis")

    mode = st.radio(
        "Choose Analysis Type",
        ["Correlation & Time Delay", "Template Matching"]
    )

    if mode == "Correlation & Time Delay":
        correlation_ui(display_mode)

    elif mode == "Template Matching":
        template_matching_ui(display_mode)


def correlation_ui(display_mode):
    st.subheader("Correlation & Time Delay")

    uploaded_files = st.file_uploader(
        "Upload exactly TWO signal files",
        type=["txt"],
        accept_multiple_files=True,
        key="corr_files"
    )

    signals = []
    if uploaded_files:
        for f in uploaded_files:
            indices, values = read_signal(f)
            signals.append((indices, values))
            st.write(f"Loaded `{f.name}` with {len(values)} samples")
            plot_signal(indices, values, title=f.name, mode=display_mode)

    if len(signals) != 2:
        st.info("Please upload exactly two signals.")
        return

    # Ask user for sampling frequency
    Fs = st.number_input("Enter the sampling frequency (Hz)", min_value=1.0, value=100.0)

    (i1, x), (i2, h) = signals
    x = np.array(x, dtype=float)
    h = np.array(h, dtype=float)

    corr_indices, corr_values = normalized_correlation(x, h)

    st.subheader("Correlation Output")
    plot_signal(corr_indices, corr_values, "Correlation Result", mode=display_mode)

    # Time delay
    lag_index = np.argmax(np.abs(corr_values))
    lag_samples = corr_indices[lag_index]
    time_delay = lag_samples / Fs

    st.subheader("Time Delay")
    st.write(f"Fs = {Fs} Hz")
    st.write(f"Expected output = {lag_samples}/{Fs} = {time_delay:.6f} s")

    # Optional: Compare with expected correlation
    expected_file = st.file_uploader(
        "Upload expected correlation output file (optional)",
        type=["txt"],
        key="expected_corr"
    )

    if expected_file:
        relative_path = os.path.join(
            "..", "Tasks", "Task 7", "Point1 Correlation", "CorrOutput.txt"
        )
        Compare_Signals(relative_path, corr_indices, corr_values)


def template_matching_ui(display_mode):

    st.subheader("Template Matching (EOG Classification)")

    st.write("""
    - **Class 1** → Down movement  
    - **Class 2** → Up movement  
    """)

    class1_path = os.path.join("..", "Tasks", "Task 7", "point3 Files", "Class 1")
    class2_path = os.path.join("..", "Tasks", "Task 7", "point3 Files", "Class 2")

    class1_signals = load_signals_from_folder(class1_path)
    class2_signals = load_signals_from_folder(class2_path)

    if len(class1_signals) == 0 or len(class2_signals) == 0:
        st.error("Training folders are empty!")
        return

    test_file = st.file_uploader(
        "Upload Test Signal",
        type=["txt"],
        key="test_file"
    )

    if not test_file:
        return

    test_signal = read_uploaded_values_only(test_file)
    indices = np.arange(len(test_signal))

    plot_signal(indices, test_signal, "Test Signal", mode=display_mode)

    label, c1, c2 = classify_signal_avg_max(
        test_signal,
        class1_signals,
        class2_signals
    )

    st.subheader("Classification Result")
    # st.write(f"Avg Max Corr with Class 1 (Down): **{c1:.3f}**")
    # st.write(f"Avg Max Corr with Class 2 (Up): **{c2:.3f}**")
    st.success(f"Predicted Class: **{label}**")
