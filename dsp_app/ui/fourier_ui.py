import streamlit as st
import numpy as np
from io import StringIO
from utils.dft_utils import smart_fourier, compute_amplitude_phase
from utils.plot_utils import plot_signal
from utils.dft_test_utils import read_docx_amp_phase, run_dft_tests
import tempfile


def fourier_tab(display_mode):
    st.header("Fourier Transform (DFT / IDFT)")

    st.markdown("Upload a signal file (text). Format: `<index> <value>` per line (headers are ignored).")
    uploaded_file = st.file_uploader("Upload a signal file", type=["txt"], accept_multiple_files=False)

    # Optional: example file path (developer note: convert local path to URL when needed)
    # SAMPLE_FILE = "/mnt/data/Screenshot 2025-11-22 022313.png"  # example from environment (not a signal file)
    # If you want to load a file by path in the environment, you can read it similarly.

    if not uploaded_file:
        st.info("Please upload a .txt signal file to continue.")
        return

    indices, samples = _parse_signal_file(uploaded_file)
    if not samples:
        st.error("Couldn't parse any numeric samples from the file. Check the file format.")
        return

    # Force numpy array of floats
    samples = np.asarray(samples, dtype=float)
    indices = list(indices)

    st.subheader("Original Signal")
    plot_signal(indices, samples, title="Input Signal", mode=display_mode)

    fs = st.number_input("Sampling frequency (Hz)", min_value=1.0, value=1000.0, step=1.0)


    use_fft = st.checkbox("Use FFT", value=False)
    # Compute DFT
    X = smart_fourier(samples, inverse=False, use_fft=use_fft)
    amp, ph = compute_amplitude_phase(X, unwrap_phase=False)
   

    N = samples.shape[0]
    # frequency axis using numpy FFT frequencies so it matches DFT bins: freqs = k * fs / N
    freqs = np.arange(N) * (fs / N)

    st.subheader("Frequency Domain")
    plot_signal(freqs, amp, title="Amplitude Spectrum", mode="Continuous")
    plot_signal(freqs, ph, title="Phase Spectrum", mode="Continuous")
    
    
    st.markdown("---")
    st.subheader("DFT Output Testing")

    expected_file = st.file_uploader("Upload Expected Amplitude/Phase DOCX", type=["docx"], key="dft_test")

    if expected_file is not None:
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        temp.write(expected_file.read())
        temp.close()

        # teacher expected values
        expected_amp, expected_phase = read_docx_amp_phase(temp.name)
        
        
        amp_for_test = [round(a, 13) for a in amp]
        ph_for_test  = [round(p, 13) for p in ph]

        expected_amp_r = [round(a, 13) for a in expected_amp]
        expected_phase_r = [round(p, 13) for p in expected_phase]


        amp_ok, phase_ok = run_dft_tests(expected_amp_r, expected_phase_r,amp_for_test, ph_for_test)
        
        
        if amp_ok:
            st.success("Amplitude Test: PASSED")
        else:
            st.error("Amplitude Test: FAILED")

        if phase_ok:
            st.success("Phase Test: PASSED")
        else:
            st.error("Phase Test: FAILED")
            
    # Reconstruction
    st.markdown("---")
    st.subheader("Reconstruct signal (IDFT)")

    if st.button("Reconstruct using IDFT"):
        rec = smart_fourier(X, inverse=True, use_fft=use_fft)
        # numerical tiny imaginary parts may exist; drop them
        rec_real = np.real_if_close(rec, tol=1000)  # promote to real if imag tiny
        rec_real = np.real(rec_real)
        # Round to a reasonable number of decimals to avoid test exact-equality curiosity
        rec_real = np.round(rec_real, 8)

        
        plot_signal(indices, rec_real, title="Reconstructed Signal (IDFT)", mode=display_mode)

        # Precise comparison using tolerance
        if np.allclose(samples, rec_real, rtol=0, atol=1e-6):
            st.success("Reconstruction matches original.")
        else:
            # show max error and where it occurs
            diffs = np.abs(samples - rec_real)
            max_err = float(np.max(diffs))
            idx = int(np.argmax(diffs))
            st.warning(f"Reconstruction differs. max abs error = {max_err:.4e} at index {idx}.")
            st.write("Original sample, Reconstructed sample, difference at that index:")
            st.write(float(samples[idx]), float(rec_real[idx]), float(diffs[idx]))

       
