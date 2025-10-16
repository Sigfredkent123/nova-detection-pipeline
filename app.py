# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import sys
import subprocess
import json
import os
from pathlib import Path
from PIL import Image

# -------------------------
# Setup
# -------------------------
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="NoVA-SCAN", layout="wide")


# -------------------------
# Utility: find first valid JSON in text
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
                    candidate = text[start_idx : i + 1]
                    return candidate  # raw string
    return None


def extract_json_from_process_result(proc):
    for stream_text in [proc.stdout, proc.stderr]:
        candidate_str = find_first_json(stream_text)
        if candidate_str:
            try:
                return json.loads(candidate_str)
            except Exception as e:
                return {"error": f"Failed to parse JSON: {str(e)}"}
    return {"error": "No JSON output found from subprocess"}


# -------------------------
# Run detection subprocess
# -------------------------
def run_model(script_path, image_path, save_dir, timeout=120):
    if not os.path.exists(script_path):
        st.error(f"Script not found: {script_path}")
        return None

    try:
        proc = subprocess.run(
            [sys.executable, script_path, image_path, str(save_dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        st.error(f"Model process timed out after {timeout}s.")
        return None

    result = extract_json_from_process_result(proc)
    if result:
        return result

    # Debug output if parsing failed
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
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_path = OUTPUT_DIR / f"{option.lower()}_input.png"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button(f"Run {option} Detection"):
        script_map = {
            "Eyes": "nova_eye.py",  # full OpenCV script
            "Palm": "finalpalm.py",
            "Nails": "nova_nail.py",
        }

        save_dir = OUTPUT_DIR / option.lower()
        save_dir.mkdir(exist_ok=True)

        with st.spinner(f"Running {option} detection..."):
            results = run_model(script_map[option], str(image_path), save_dir)

        if results:
            st.success(f"{option} detection completed!")

            # Ensure results is always a dict
            if not isinstance(results, dict):
                results = {"results": results}

            # Annotated image
            annotated = results.get("annotated_image")
            if annotated and os.path.exists(annotated):
                st.image(annotated, caption="Annotated Image", use_column_width=True)
                with open(annotated, "rb") as f:
                    st.download_button(
                        "Download annotated image", f, file_name=os.path.basename(annotated)
                    )

            # ZIP of crops
            zip_file = results.get("zip_file")
            if zip_file and os.path.exists(zip_file):
                with open(zip_file, "rb") as f:
                    st.download_button(
                        "Download crops ZIP", f, file_name=os.path.basename(zip_file)
                    )

            # Show results in JSON
            st.json(results)
