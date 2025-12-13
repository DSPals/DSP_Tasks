# ui/filter_ui.py
import streamlit as st
import numpy as np

from utils.filtering import (
    design_fir_from_spec,
    save_coeffs_like_example,
    filter_time_domain,
    filter_freq_domain,
)
from utils.file_utils import read_signal   
from utils.plot_utils import plot_signal
from utils.tests import Compare_Signals
from utils.file_utils import parse_expected_coeffs  


def filtering_tab(display_mode):

    st.header("FIR Filter Design & Test")

    st.subheader("1) Upload Filter Specification (.txt)")
    spec_file = st.file_uploader("Upload FilterSpecifications.txt", type=["txt"])

    st.subheader("2) (Optional) Upload Input Signal to Filter (.txt)")
    signal_file = st.file_uploader("Upload InputSignal.txt", type=["txt"])

    st.subheader("3) Upload Expected Coefficients for Testing ")
    expected_file = st.file_uploader("Coefficients.txt", type=["txt"])

    if st.button("Generate Filter"):

        if not spec_file:
            st.error("Please upload FilterSpecifications.txt")
            return

        # ----------------------------
        # Save uploaded spec & expected files
        # ----------------------------
        spec_path = "uploaded_spec.txt"
        with open(spec_path, "wb") as f:
            f.write(spec_file.getbuffer())

        expected_path = None
        if expected_file:
            expected_path = "uploaded_expected_coeffs.txt"
            with open(expected_path, "wb") as f:
                f.write(expected_file.getbuffer())

        # ----------------------------
        # Design filter from spec file
        # ----------------------------
        try:
            indices, h_generated, N = design_fir_from_spec(spec_path)
        except Exception as e:
            st.error(f"Error designing filter: {e}")
            return

        st.write(f"**Generated Filter (N = {N})**")
        # show small table
        df_preview = { "n": indices, "h[n]": [float("{:.10g}".format(x)) for x in h_generated] }
        st.dataframe(df_preview)

        # ----------------------------
        # Save coefficients to text file and provide download
        # ----------------------------
        save_path = "GeneratedFilterCoeffs.txt"
        save_coeffs_like_example(save_path, indices, h_generated)
        st.success(f"Generated filter coefficients saved as **{save_path}**")
        with open(save_path, "rb") as f:
            st.download_button("Download Generated Coefficients", f, file_name=save_path)

        # ----------------------------
        # If expected file supplied: compare coefficients
        # ----------------------------
        if expected_path:
            st.subheader("Coefficient Comparison")
            # parse_expected_coeffs should accept a path or file-like; your version used file object, adapt:
            try:
                # If parse_expected_coeffs accepts a filename string:
                exp_indices, exp_samples = parse_expected_coeffs(expected_path)
            except Exception:
                # If parse_expected_coeffs expects uploaded_file, try reading from uploaded file object
                expected_file.seek(0)
                exp_indices, exp_samples = parse_expected_coeffs(expected_file)

            st.write("Expected N = ", len(exp_samples))
            # Use your existing Compare_Signals function (it reads file path)
            Compare_Signals(expected_path, indices, h_generated)

        # ----------------------------
        # If user uploaded an input signal: filter it both ways & plot
        # ----------------------------
        if signal_file:
            # Save the uploaded signal file
            sig_path = "uploaded_input_signal.txt"
            with open(sig_path, "wb") as f:
                f.write(signal_file.getbuffer())

            try:
                sig_indices, sig_samples = read_signal(sig_path)  # adapt to your read_signal signature
                sig_samples = np.array(sig_samples, dtype=float)
            except Exception as e:
                st.error(f"Error reading uploaded signal: {e}")
                return

            st.subheader("Filtering Input Signal (both methods)")

            td_idx, td_out = filter_time_domain(sig_indices, sig_samples, h_generated)
            fd_idx, fd_out = filter_freq_domain(sig_indices, sig_samples, h_generated)

            # Plot original
            st.write("Original Signal")
            plot_signal(sig_indices, sig_samples, title="Original", mode=display_mode)

            # Plot time-domain filtered
            st.write("Time-domain (convolution) result")
            plot_signal(td_idx, td_out, title="Filtered (Time Domain)", mode=display_mode)

            # Plot freq-domain filtered
            st.write("Freq-domain (DFT multiply) result")
            plot_signal(fd_idx, fd_out, title="Filtered (Freq Domain)", mode=display_mode)

            # numeric compare between td_out and fd_out
            min_len = min(len(td_out), len(fd_out))
            max_diff = float(np.max(np.abs(np.array(td_out[:min_len]) - np.array(fd_out[:min_len]))))
            #st.write(f"Max abs difference between time/freq methods (first {min_len} samples): {max_diff:.6g}")
            if max_diff < 1e-2:
                st.success("Time-domain and Frequency-domain outputs MATCH within tolerance.")
            else:
                st.warning("Time-domain and Frequency-domain outputs differ — check implementations.")

            # Offer downloads for filtered outputs
            td_save = "filtered_time_domain.txt"
            fd_save = "filtered_freq_domain.txt"

            # Save as simple index/value text
            with open(td_save, "w") as f:
                for i, v in zip(td_idx, td_out):
                    f.write(f"{i} {v}\n")
            with open(fd_save, "w") as f:
                for i, v in zip(fd_idx, fd_out):
                    f.write(f"{i} {v}\n")

            with open(td_save, "rb") as f:
                st.download_button("Download Time-Domain Filtered Output", f, file_name=td_save)
            with open(fd_save, "rb") as f:
                st.download_button("Download Freq-Domain Filtered Output", f, file_name=fd_save)





