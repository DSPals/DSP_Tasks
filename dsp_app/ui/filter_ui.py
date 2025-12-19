# ui/filter_ui.py
import streamlit as st
import numpy as np

from utils.filtering import (
    design_fir_from_spec,
    save_coeffs_like_example,
    filter_time_domain,
    filter_freq_domain,
)
from utils.file_utils import read_signal, parse_expected_coeffs
from utils.plot_utils import plot_signal
from utils.tests import Compare_Signals


def filtering_tab(display_mode):

    st.header("FIR Filter Design & Test")

    st.subheader("1) Upload Filter Specification (.txt)")
    spec_file = st.file_uploader("FilterSpecifications.txt", type=["txt"])

    st.subheader("2) (Optional) Upload Input Signal (.txt)")
    signal_file = st.file_uploader("InputSignal.txt", type=["txt"])

    st.subheader("3) Upload Expected Output (.txt)")
    expected_file = st.file_uploader("Expected Output File", type=["txt"])

    if st.button("Generate Filter"):

        if not spec_file:
            st.error("Please upload FilterSpecifications.txt")
            return

        if not expected_file:
            st.error("Please upload Expected Output file")
            return

        # -------------------------------------------------
        # Save uploaded files
        # -------------------------------------------------
        spec_path = "spec.txt"
        with open(spec_path, "wb") as f:
            f.write(spec_file.getbuffer())

        expected_path = "expected.txt"
        with open(expected_path, "wb") as f:
            f.write(expected_file.getbuffer())

        # -------------------------------------------------
        # Design FIR filter
        # -------------------------------------------------
        try:
            indices, h_generated, N = design_fir_from_spec(spec_path)
        except Exception as e:
            st.error(f"Error designing filter: {e}")
            return

        st.success(f"Generated Filter (N = {N})")

        # Show coefficients preview
        st.dataframe({
            "n": indices,
            "h[n]": [float("{:.10g}".format(x)) for x in h_generated]
        })

        # Save coefficients
        coeff_path = "GeneratedFilterCoeffs.txt"
        save_coeffs_like_example(coeff_path, indices, h_generated)

        with open(coeff_path, "rb") as f:
            st.download_button(
                "Download Generated Filter Coefficients",
                f,
                file_name=coeff_path
            )

        # =================================================
        # CASE 1: FILTER DESIGN ONLY (no signal uploaded)
        # =================================================
        if signal_file is None:
            st.subheader("Coefficient Comparison (Filter Design Only)")
            with open(expected_path, "rb") as f:
                exp_indices, exp_samples = parse_expected_coeffs(f)
                
            st.write("Expected N =", len(exp_samples))

            Compare_Signals(expected_path, indices, h_generated)
            return

        # =================================================
        # CASE 2: FILTER APPLICATION (signal uploaded)
        # =================================================
        sig_path = "input_signal.txt"
        with open(sig_path, "wb") as f:
            f.write(signal_file.getbuffer())

        try:
            sig_indices, sig_samples = read_signal(sig_path)
            sig_samples = np.array(sig_samples, dtype=float)
        except Exception as e:
            st.error(f"Error reading input signal: {e}")
            return

        st.subheader("Filtering Input Signal")

        td_idx, td_out = filter_time_domain(
            sig_indices, sig_samples, h_generated
        )
        fd_idx, fd_out = filter_freq_domain(
            sig_indices, sig_samples, h_generated
        )

        # Plot signals
        plot_signal(sig_indices, sig_samples,
                    title="Original Signal", mode=display_mode)

        plot_signal(td_idx, td_out,
                    title="Filtered Signal (Time Domain)", mode=display_mode)

        plot_signal(fd_idx, fd_out,
                    title="Filtered Signal (Frequency Domain)", mode=display_mode)

        # Compare TD vs FD
        min_len = min(len(td_out), len(fd_out))
        max_diff = float(
            np.max(np.abs(
                np.array(td_out[:min_len]) -
                np.array(fd_out[:min_len])
            ))
        )

        if max_diff < 1e-2:
            st.success("Time-domain and Frequency-domain outputs MATCH.")
        else:
            st.warning("Time-domain and Frequency-domain outputs differ.")

        # ✅ Correct comparison: filtered signal
        st.subheader("Filtered Signal Test Case")
        Compare_Signals(expected_path, td_idx, td_out)

        # Save filtered outputs
        with open("filtered_time_domain.txt", "w") as f:
            for i, v in zip(td_idx, td_out):
                f.write(f"{i} {v}\n")

        with open("filtered_freq_domain.txt", "w") as f:
            for i, v in zip(fd_idx, fd_out):
                f.write(f"{i} {v}\n")
