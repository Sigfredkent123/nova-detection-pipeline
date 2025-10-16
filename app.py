# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import subprocess, json, os
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def run_model(script, image_path, save_dir):
    """Run a model and return parsed JSON output."""
    result = subprocess.run(
        ["python", script, image_path, str(save_dir)],
        capture_output=True, text=True
    )
    try:
        detections = json.loads(result.stdout)
        return detections
    except json.JSONDecodeError:
        st.error("Could not parse JSON output.")
        st.text(result.stdout)
        return None

st.set_page_config(page_title="NOVA Detection Suite", layout="centered")
st.title("🧠 NOVA Detection Pipeline")
st.markdown("Detect **eye/conjunctiva**, **palm**, and **nail** regions using Roboflow models.")

# === EYE DETECTION ===
st.header("👁️ Eye / Conjunctiva Detection")
eye_file = st.file_uploader("Upload Eye Image", type=["jpg", "jpeg", "png"])
if eye_file:
    eye_path = OUTPUT_DIR / "eye_input.png"
    with open(eye_path, "wb") as f:
        f.write(eye_file.getbuffer())

    if st.button("Run Eye Detection"):
        eye_dir = OUTPUT_DIR / "eye"
        eye_dir.mkdir(exist_ok=True)
        eye_results = run_model("nova_eye.py", str(eye_path), eye_dir)
        if eye_results:
            st.image(Image.open(eye_results["annotated_image"]), caption="Annotated Eye Detection")
            st.json(eye_results)

# === PALM DETECTION ===
st.header("✋ Palm Detection")
palm_file = st.file_uploader("Upload Palm Image", type=["jpg", "jpeg", "png"])
if palm_file:
    palm_path = OUTPUT_DIR / "palm_input.png"
    with open(palm_path, "wb") as f:
        f.write(palm_file.getbuffer())

    if st.button("Run Palm Detection"):
        palm_dir = OUTPUT_DIR / "palm"
        palm_dir.mkdir(exist_ok=True)
        palm_results = run_model("finalpalm.py", str(palm_path), palm_dir)
        if palm_results:
            st.image(palm_results["annotated_image"], caption="Annotated Palm Detection")
            st.json(palm_results)

# === NAIL DETECTION ===
st.header("💅 Nail Detection")
nail_file = st.file_uploader("Upload Nail Image", type=["jpg", "jpeg", "png"])
if nail_file:
    nail_path = OUTPUT_DIR / "nail_input.png"
    with open(nail_path, "wb") as f:
        f.write(nail_file.getbuffer())

    if st.button("Run Nail Detection"):
        nail_dir = OUTPUT_DIR / "nail"
        nail_dir.mkdir(exist_ok=True)
        nail_results = run_model("nova_nail.py", str(nail_path), nail_dir)
        if nail_results:
            st.image(Image.open(nail_results["annotated_image"]), caption="Annotated Nail Detection")
            st.json(nail_results)

# === COMBINED RESULTS ===
st.header("🧾 Combined JSON Output")
if st.button("Generate Combined Report"):
    combined = {}
    for name in ["eye", "palm", "nail"]:
        result_file = OUTPUT_DIR / name / "annotated_*"
    combined_path = OUTPUT_DIR / "combined_results.json"
    if os.path.exists(combined_path):
        with open(combined_path) as f:
            combined = json.load(f)
        st.download_button("Download Combined JSON", json.dumps(combined, indent=2), "combined_results.json")
