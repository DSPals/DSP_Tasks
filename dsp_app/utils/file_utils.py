import numpy as np
import io
import streamlit as st


def _parse_signal_file(uploaded_file):
    """
    Robust parser for your signal files. Many of your test files have 3 header lines
    then lines like: "<index> <value>" possibly with tabs.
    Returns (indices_list, samples_list) where samples_list are floats.
    """
    # uploaded_file is a streamlit UploadedFile or a path-like object with .read()
    content_bytes = uploaded_file.read()
    # reset file pointer for Streamlit after reading (so other code can read again)
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    # decode
    try:
        s = content_bytes.decode("utf-8")
    except Exception:
        s = content_bytes.decode("latin-1")

    lines = [ln.strip() for ln in s.splitlines() if ln.strip() != ""]

    # many test files have some header lines — try to locate first data line that contains two tokens.
    data_lines = []
    for ln in lines:
        parts = ln.split()
        # Accept lines with 2 tokens where first token is int-like and second is number-like
        if len(parts) >= 2:
            # sometimes there are extra non-data lines; try parseability
            try:
                _idx = int(parts[0])
                _val = float(parts[1])
                data_lines.append((parts[0], parts[1]))
            except Exception:
                # skip
                continue

    if not data_lines:
        # fallback: maybe file contains a single column of samples
        numeric = []
        for ln in lines:
            try:
                numeric.append(float(ln))
            except Exception:
                continue
        if numeric:
            indices = list(range(len(numeric)))
            samples = numeric
            return indices, samples

        # nothing usable
        return [], []

    indices = []
    samples = []
    for a, b in data_lines:
        indices.append(int(a))
        samples.append(float(b))

    return indices, samples


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
