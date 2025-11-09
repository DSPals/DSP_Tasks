import streamlit as st
from ui.operations_ui import operations_tab
from ui.generation_ui import generation_tab
from ui.quantization_ui import quantization_tab

st.set_page_config(page_title="DSP Signal Processor", layout="wide")

st.title("DSP Signal Processor")

menu = st.sidebar.radio("Main Menu", ["Signal Operations", "Signal Generation", "Quantization"])
display_mode = st.sidebar.selectbox("Display Mode", ["Discrete", "Continuous", "Discrete + Continuous"])

if menu == "Signal Operations":
    operations_tab(display_mode)
elif menu == "Signal Generation":
    generation_tab(display_mode)
elif menu == "Quantization":
    quantization_tab(display_mode)
