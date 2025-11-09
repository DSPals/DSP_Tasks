import numpy as np
import io
import streamlit as st

def read_signal(file):
    """Read a signal from a txt file (uploaded or path)."""
    if hasattr(file, "read"):
        content = file.read().decode("utf-8").strip().split("\n")
    else:
        with open(file, "r") as f:
            content = f.read().strip().split("\n")

    content = [line.strip() for line in content if line.strip()]
    start_idx = next((i for i, l in enumerate(content) if len(l.split()) == 2), None)
    if start_idx is None:
        raise ValueError("No valid signal data found.")

    data = [list(map(float, line.split())) for line in content[start_idx:]]
    indices, values = zip(*data)
    return np.array(indices), np.array(values)

def download_signal(indices, values, label="Download", default_name="output.txt"):
    buffer = io.StringIO()
    buffer.write(f"{len(values)}\n")
    for i, v in zip(indices, values):
        buffer.write(f"{i} {v}\n")
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=default_name,
        mime="text/plain"
    )
