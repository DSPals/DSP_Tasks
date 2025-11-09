import numpy as np
import io
import streamlit as st

def read_signal(file):
    """Read a signal from a txt file (uploaded or path). 
    Returns integer indices and float values.
    """

    if hasattr(file, "read"):
        content = file.read().decode("utf-8").strip().split("\n")
    else:
        with open(file, "r") as f:
            content = f.read().strip().split("\n")

    content = [line.strip() for line in content if line.strip()]

    # --- Find where the numeric data starts (skip headers if any) ---
    start_idx = next((i for i, l in enumerate(content) if len(l.split()) == 2), None)
    if start_idx is None:
        raise ValueError("No valid signal data found (must be two columns).")

    # --- Parse data (int index, float value) ---
    indices = []
    values = []
    for line in content[start_idx:]:
        parts = line.split()
        if len(parts) == 2:
            try:
                idx = int(float(parts[0]))  # allow '0.0' to become 0
                val = float(parts[1])
                indices.append(idx)
                values.append(val)
            except ValueError:
                continue  

    return np.array(indices, dtype=int), np.array(values, dtype=float)



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
