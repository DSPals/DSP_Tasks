import streamlit as st
import numpy as np
from utils.convolution import (
    moving_average,
    first_derivative,
    second_derivative,
    manual_convolution,
)
from utils.file_utils import read_signal
from utils.plot_utils import plot_signal
from utils.tests import CompareSignals_Convolution

def Convolution_tab(display_mode):

    st.header("Signal Convolution")

    operation = st.radio(
        "Select operation:",
        ["Moving Average", "Derivative", "Convolution"],
        horizontal=True,
    )

    uploaded_files = st.file_uploader(
        "Upload signal files", type=["txt"], accept_multiple_files=True
    )
    signals = []
    if uploaded_files:
        for f in uploaded_files:
            indices, values = read_signal(f)
            signals.append((indices, values))
            st.write(f"Loaded `{f.name}` with {len(values)} samples")
            plot_signal(indices, values, title=f.name, mode=display_mode)

    if not signals:
        return

    if operation == "Moving Average":
        st.subheader("Moving Average")
        window = st.number_input("Enter window size (M):", min_value=1, value=3, step=1)
        indices, values = signals[0]
        y = moving_average(values, window)
        y_indices = indices[: len(y)]
        plot_signal(y_indices, y, title="Moving Average Output", mode=display_mode)
        
        if window == 3:
            CompareSignals_Convolution("Moving Average 1",y_indices,y)
        elif window == 5:
            CompareSignals_Convolution("Moving Average 2",y_indices,y)

    elif operation == "Derivative":
        st.subheader("Derivative Options")
        choice = st.radio("Select derivative type:", ["First", "Second"], horizontal=True)
        indices, values = signals[0]

        if choice == "First":
            y = first_derivative(values)
            y_indices = indices[:-1]
            title = "First Derivative Output"

        else:
            y = second_derivative(values)
            y_indices = indices[:-2]
            title = "Second Derivative Output"

        plot_signal(y_indices, y, title=title, mode=display_mode)

        if choice == "First":
            CompareSignals_Convolution("Derivative 1",y_indices,y)
        elif choice == "Second":
            CompareSignals_Convolution("Derivative 2",y_indices,y)

    elif operation == "Convolution":
        st.subheader("Convolution of Two Signals")
        if len(signals) < 2:
            st.warning("Please upload two signals for convolution.")
            return
        indices_x, x = signals[0]
        indices_h, h = signals[1]
        y = manual_convolution(x, h)
        y_indices = list(range(min(indices_x) + min(indices_h),
                                min(indices_x) + min(indices_h) + len(y)))
        plot_signal(y_indices, y, title="Convolution Output", mode=display_mode)
        CompareSignals_Convolution("Convolution",y_indices,y)

