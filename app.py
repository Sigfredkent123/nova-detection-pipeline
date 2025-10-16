# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import subprocess, json, os, re
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ======== PAGE CONFIG ========
st.set_page_config(page_title="NoVA-SCAN", layout="wide")

# ======== Helper: Extract JSON from any stdout ========
def extract_json(text):
    """Extract the first valid JSON object from mixed stdout text."""
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    match = json_pattern.search(text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

def run_model(script, image_path, save_dir):
    """Run a detection script and parse its JSON output safely."""
    result = subprocess.run(
        ["python", script, image_path, str(save_dir)],
        capture_output=True, text=True
    )
    detections = extract_json(result.stdout)
    if not detections:
        st.error("❌ Model output not valid JSON.")
        st.text(result.stdout)  # show debug
    return detections

# ======== STYLES ========
st.markdown("""
<style>
body {background-color: #f8faff;}
h1, h2, h3, h4 {color: #002b5b;}
.section {background: white; border-radius: 15px; padding: 2rem; margin-top: 1.5rem; 
box-shadow: 0 2px 10px rgba(0,0,0,0.1);}
.center {text-align: center;}
.button-primary {background-color: #2563eb; color: white; padding: 0.8rem 2rem; border-radius: 25px; text-decoration: none;}
.card {background: #f4f7ff; border-radius: 12px; padding: 1rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ======== HEADER ========
st.markdown("<h1 class='center'>🔬 What is NoVA-SCAN</h1>", unsafe_allow_html=True)
st.write("""
NoVA-Scan is an **AI-powered web application** that detects key areas 
from your images — the **Eyes**, **Palm**, and **Nail Beds** — using YOLO object detection.
""")

# ======== Upload + Detection Interface ========
st.markdown("<hr>", unsafe_allow_html=True)
st.header("🧠 Run NoVA Detection")

option = st.selectbox("Choose Detection Type:", ["Eyes", "Palm", "Nails"])
file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if file:
    image_path = OUTPUT_DIR / f"{option.lower()}_input.png"
    with open(image_path, "wb") as f:
        f.write(file.getbuffer())

    if st.button(f"🚀 Run {option} Detection"):
        script_map = {
            "Eyes": "nova_eye.py",
            "Palm": "finalpalm.py",
            "Nails": "nova_nail.py"
        }
        save_dir = OUTPUT_DIR / option.lower()
        save_dir.mkdir(exist_ok=True)
        with st.spinner(f"Running {option} model... please wait"):
            results = run_model(script_map[option], str(image_path), save_dir)

        if results:
            st.success(f"✅ {option} detection completed!")
            st.image(results["annotated_image"], caption=f"{option} Detection Result", use_column_width=True)
            st.download_button("⬇️ Download Annotated Image",
                               open(results["annotated_image"], "rb"),
                               file_name=os.path.basename(results["annotated_image"]))
            if "zip_file" in results and os.path.exists(results["zip_file"]):
                st.download_button("📦 Download Cropped ZIP",
                                   open(results["zip_file"], "rb"),
                                   file_name=os.path.basename(results["zip_file"]))
            st.json(results)

st.markdown("<p class='center' style='margin-top:3rem;'>See. Scan. Detect. — the NoVA way.</p>", unsafe_allow_html=True)
