# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import sys
import subprocess, json, os
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="NoVA-SCAN", layout="wide")


# -------------------------
# Utility: find balanced JSON
# -------------------------
def find_first_json(text: str):
    if not text:
        return None
    start_idx = None
    depth = 0
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    candidate = text[start_idx:i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        start_idx = None
                        depth = 0
    return None


def extract_json_from_process_result(proc):
    for stream_text, name in [(proc.stdout, "stdout"), (proc.stderr, "stderr")]:
        candidate = find_first_json(stream_text)
        if candidate:
            try:
                return json.loads(candidate)
            except Exception:
                pass
    return None


# -------------------------
# Run model with robust parsing
# -------------------------
def run_model(script, image_path, save_dir, timeout=120):
    if not os.path.exists(script):
        st.error(f"Script not found: {script}")
        return None

    try:
        proc = subprocess.run(
            [sys.executable, script, image_path, str(save_dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        st.error(f"Model process timed out after {timeout}s.")
        return None

    parsed = extract_json_from_process_result(proc)
    if parsed:
        return parsed

    st.error("❌ Model output not valid JSON (couldn't extract JSON from process output).")
    st.markdown(f"**Subprocess return code:** `{proc.returncode}`")
    if proc.stdout.strip():
        st.markdown("**--- Stdout ---**")
        st.code(proc.stdout[:10000])
    if proc.stderr.strip():
        st.markdown("**--- Stderr ---**")
        st.code(proc.stderr[:10000])
    return None


# -------------------------
# Streamlit UI
# -------------------------
st.title("NoVA-SCAN — Run Detection")

option = st.selectbox("Choose Detection Type:", ["Eyes", "Palm", "Nails"])
file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if file:
    image_path = OUTPUT_DIR / f"{option.lower()}_input.png"
    with open(image_path, "wb") as f:
        f.write(file.getbuffer())

    if st.button(f"Run {option} Detection"):
        script_map = {
            "Eyes": "nova_eye.py",      # headless script
            "Palm": "finalpalm.py",
            "Nails": "nova_nail.py"
        }
        save_dir = OUTPUT_DIR / option.lower()
        save_dir.mkdir(exist_ok=True)

        with st.spinner("Running model..."):
            results = run_model(script_map[option], str(image_path), save_dir)

        if results:
            st.success(f"{option} detection completed!")
            annotated = results.get("annotated_image")
            if annotated and os.path.exists(annotated):
                st.image(annotated, caption="Annotated Image", use_column_width=True)
                with open(annotated, "rb") as f:
                    st.download_button(
                        "Download annotated image", f, file_name=os.path.basename(annotated)
                    )

            z = results.get("zip_file")
            if z and os.path.exists(z):
                with open(z, "rb") as f:
                    st.download_button(
                        "Download crops ZIP", f, file_name=os.path.basename(z)
                    )

            st.json(results)
