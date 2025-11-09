import streamlit as st
from utils.file_utils import read_signal, download_signal
from utils.plot_utils import plot_signal, plot_multiple_signals
from utils.signal_ops import add_signals, multiply_signal, subtract_signals, shift_signal, fold_signal
from utils.tests import AddSignalSamplesAreEqual, SubSignalSamplesAreEqual, MultiplySignalByConst, ShiftSignalByConst, Folding

def operations_tab(display_mode):
    uploaded_files = st.file_uploader("Upload signal files", type=["txt"], accept_multiple_files=True)
    signals = []
    if uploaded_files:
        for f in uploaded_files:
            indices, values = read_signal(f)
            signals.append((indices, values))
            st.write(f"Loaded `{f.name}` with {len(values)} samples")
            plot_signal(indices, values, title=f.name, mode=display_mode)

    if not signals:
        return

    option = st.selectbox(
        "Choose Operation",
        ["Add Signals", "Multiply Signal by Constant", "Subtract Signals", "Delay/Advance", "Fold/Reverse", "Signals at the Same Time"]
    )

    if option == "Add Signals" and len(signals) > 1:
        indices, result = add_signals(signals)
        plot_signal(indices, result, "Added Signal", mode=display_mode)
        download_signal(indices, result, "Download Added Signal", "added_signal.txt")
        AddSignalSamplesAreEqual("Signal1.txt", "Signal2.txt", indices, result)

    elif option == "Multiply Signal by Constant":
        k = st.number_input("Enter constant (k):", value=5.0)
        indices, result = multiply_signal(signals[0], k)
        plot_signal(indices, result, f"Signal * {k}", mode=display_mode)
        download_signal(indices, result, f"Download Signal * {k}", f"signal_times_{k}.txt")
        MultiplySignalByConst(5, indices, result)

    elif option == "Subtract Signals" and len(signals) > 1:
        indices, result = subtract_signals(signals)
        plot_signal(indices, result, "Subtracted Signal", mode=display_mode)
        download_signal(indices, result, "Download Subtracted Signal", "subtracted_signal.txt")
        SubSignalSamplesAreEqual("Signal1.txt", "Signal2.txt", indices, result)

    elif option == "Delay/Advance":
        k = st.number_input("Enter shift value (k):", value=-3)
        indices, result = shift_signal(signals[0], k)
        plot_signal(indices, result, f"Signal shifted by {k}", mode=display_mode)
        download_signal(indices, result, "Download Shifted Signal", f"signal_shifted_{k}.txt")
        ShiftSignalByConst(k, indices, result)

    elif option == "Fold/Reverse":
        indices, result = fold_signal(signals[0])
        plot_signal(indices, result, "Folded Signal", mode=display_mode)
        download_signal(indices, result, "Download Folded Signal", "folded_signal.txt")
        Folding(indices, result)

    elif option == "Signals at the Same Time" and len(signals) >= 2:
        labeled_signals = [
            (indices, values, uploaded_files[i].name if i < len(uploaded_files) else f"Signal {i+1}")
            for i, (indices, values) in enumerate(signals)
        ]
        plot_multiple_signals(labeled_signals, mode=display_mode)
