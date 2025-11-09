import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def plot_signal(indices, values, title="Signal", mode="Discrete", sample=0):
    fig, ax = plt.subplots()
    if mode == "Continuous":
        ax.plot(indices, values, label=title, color="b")
    elif mode == "Discrete":
        ax.stem(indices, values, linefmt="b-", markerfmt="bo", basefmt="k-", label=title)
    elif mode == "Discrete + Continuous":
        ax.plot(indices, values, color="b", alpha=0.6, label=f"{title} (Continuous)")
        ax.stem(indices, values, linefmt="g-", markerfmt="go", basefmt="k-", label=f"{title} (Discrete)")

    if sample == 1:
        ax.set_xlabel("n (samples)")
        ax.set_ylabel("x[n]")
    elif mode == "Continuous":
        ax.set_xlabel("t (seconds)")
        ax.set_ylabel("x[t]")
    else:
        ax.set_xlabel("n (samples)")
        ax.set_ylabel("x[n]")

    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

def plot_multiple_signals(signals, mode="Discrete"):
    fig, ax = plt.subplots()
    colors = plt.cm.tab10(np.linspace(0, 1, len(signals)))
    markers = ["o", "s", "v", "^", "D", "x", "+", "*", "p", "h"]

    for i, sig in enumerate(signals):
        if len(sig) == 3:
            indices, values, label = sig
        else:
            indices, values = sig
            label = f"Signal {i+1}"

        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]

        if mode == "Continuous":
            ax.plot(indices, values, label=label, color=color)
        elif mode == "Discrete":
            markerline, stemlines, _ = ax.stem(indices, values, basefmt="k-", label=label)
            plt.setp(markerline, color=color, marker=marker)
            plt.setp(stemlines, color=color)
        elif mode == "Discrete + Continuous":
            ax.plot(indices, values, color=color, alpha=0.6, label=f"{label} (Continuous)")
            markerline, stemlines, _ = ax.stem(indices, values, basefmt="k-", label=f"{label} (Discrete)")
            plt.setp(markerline, color=color, marker=marker)
            plt.setp(stemlines, color=color)

    ax.set_xlabel("t , n")
    ax.set_ylabel("x[t], x[n]")
    ax.set_title("All Signals Comparison")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
