import streamlit as st
from utils.signal_generation import generate_analog_signal, generate_discrete_signal
from utils.plot_utils import plot_signal

def generation_tab(display_mode):
    st.header("Signal Generation")

    wave_type = st.radio("Select Wave Type", ["Sine Wave", "Cosine Wave"], horizontal=True)
    st.markdown("### Configure Your Signal Parameters")

    col1, col2 = st.columns(2)
    with col1:
        amplitude = st.number_input("Amplitude (A)", value=1.0, step=0.1, min_value=0.0)
        phase = st.number_input("Phase Shift (θ) [radians]", value=0.0, step=0.1)
    with col2:
        analog_freq = st.number_input("Analog Frequency (Hz)", value=1.0, step=0.1, min_value=0.0)
        sampling_freq = st.number_input("Sampling Frequency (Hz)", value=10.0, step=0.1, min_value=0.0)

    duration = st.number_input("Signal Duration (seconds)", value=1.0, step=0.1, min_value=0.1)

    if sampling_freq < 2 * analog_freq:
        st.error(f"❌ Sampling frequency must be ≥ 2 × Analog Frequency (Nyquist).")
        generate_button = st.button("Generate Signal", disabled=True)
    else:
        st.success("✅ Nyquist condition satisfied.")
        generate_button = st.button("Generate Signal")

    if generate_button:
        st.info(f"Generating {wave_type.lower()} with A={amplitude}, θ={phase}, f={analog_freq}, fs={sampling_freq}, duration={duration}")
        t, analog_signal = generate_analog_signal(wave_type, amplitude, phase, analog_freq, duration)
        plot_signal(t, analog_signal, f"Analog {wave_type} (Continuous)", mode="Continuous")

        n, sampled_signal = generate_discrete_signal(wave_type, amplitude, phase, analog_freq, sampling_freq, duration)
        plot_signal(n, sampled_signal, f"Sampled {wave_type} (Discrete)", mode=display_mode, sample=1)
