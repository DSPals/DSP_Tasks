import streamlit as st
import pandas as pd
from utils.file_utils import read_signal
from utils.plot_utils import plot_signal, plot_multiple_signals
from utils.quantization import quantize_signal
from utils.tests import QuantizationTest1, QuantizationTest2

def quantization_tab(display_mode):
    st.header("Signal Quantization")

    uploaded_file = st.file_uploader("Upload a signal file", type=["txt"])
    if not uploaded_file:
        return

    indices, values = read_signal(uploaded_file)
    signal = (indices, values)
    plot_signal(indices, values, title=uploaded_file.name, mode=display_mode)

    quant_type = st.radio("Select Quantization Mode", ["By Bits", "By Levels"], horizontal=True)

    if quant_type == "By Bits":
        num_bits = st.number_input("Enter number of bits (b):", min_value=1, max_value=8, value=3, step=1)
        if st.button("Quantize Now (By Bits)"):
            _, encoded, quantized, _ = quantize_signal(signal, num_bits=num_bits)
            df = pd.DataFrame({"Index (n)": indices, "Encoded": encoded, "Quantized": quantized})
            st.dataframe(df)
            plot_multiple_signals([(indices, values, "Original"), (indices, quantized, "Quantized")], mode=display_mode)
            QuantizationTest1(encoded, quantized)

    elif quant_type == "By Levels":
        num_levels = st.number_input("Enter number of levels (L):", min_value=2, max_value=32, value=4, step=1)
        if st.button("Quantize Now (By Levels)"):
            intervals, encoded, quantized, errors = quantize_signal(signal, num_levels=num_levels)
            df = pd.DataFrame({
                "Index (n)": indices,
                "Original": values,
                "Interval": intervals,
                "Encoded": encoded,
                "Quantized": quantized,
                "Error": errors
            })
            st.dataframe(df)
            plot_multiple_signals([(indices, values, "Original"), (indices, quantized, "Quantized")], mode=display_mode)
            QuantizationTest2(intervals, encoded, quantized, errors)
