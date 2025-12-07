import streamlit as st
import numpy as np
import os
from utils.plot_utils import plot_signal
from utils.file_utils import read_signal
from utils.correlation_utils import Compare_Signals, normalized_correlation

def corr_tab(display_mode):

    st.header("Correlation")

    uploaded_files = st.file_uploader(
        "Upload exactly TWO signal files",
        type=["txt"],
        accept_multiple_files=True
    )

    signals = []
    if uploaded_files:
        for f in uploaded_files:
            indices, values = read_signal(f)
            signals.append((indices, values))
            st.write(f"Loaded `{f.name}` with {len(values)} samples")
            plot_signal(indices, values, title=f.name, mode=display_mode)

    if len(signals) != 2:
        return

    # Extract signals
    (i1, x), (i2, h) = signals
    x = np.array(x, dtype=float)
    h = np.array(h, dtype=float)

    corr_indices, corr_values = normalized_correlation(x, h)

    # Show result
    st.subheader("Correlation Output")
    plot_signal(corr_indices, corr_values, "Correlation Result", mode=display_mode)

    # Test comparison
    expected_file = st.file_uploader(
        "Upload expected correlation output file (optional)",
        type=["txt"],
        key="expected_corr"
    )

    if expected_file:
        relative_path = os.path.join("..","Tasks","Task 7", "Point1 Correlation", "CorrOutput.txt")
        Compare_Signals(relative_path, corr_indices, corr_values)

