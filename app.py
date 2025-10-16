# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import base64
import subprocess, json, os
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ======== PAGE CONFIG ========
st.set_page_config(page_title="NoVA-SCAN", layout="wide")

# ======== CUSTOM CSS ========
st.markdown("""
<style>
body {background-color: #f8faff;}
.main {padding: 0;}
h1, h2, h3, h4, h5 {color: #002b5b;}
.section {
    background: white;
    border-radius: 15px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.card {
    background: #f4f7ff;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.card img {
    border-radius: 10px;
    width: 120px;
    height: 120px;
    object-fit: cover;
}
.button-primary {
    background-color: #2563eb;
    color: white;
    padding: 0.8rem 2rem;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
}
.center {text-align: center;}
</style>
""", unsafe_allow_html=True)

# ======== HEADER ========
st.markdown("<h1 class='center'>🔬 What is NoVA-SCAN</h1>", unsafe_allow_html=True)
st.write("""
NoVA-Scan is an **AI-powered web application** that automatically detects key areas 
from your images — the **Eyes**, **Palm**, and **Nail Beds** — using advanced object detection technology (YOLO).
""")

# ======== 3 COLUMNS ========
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.image("https://i.imgur.com/Yw9eJbG.jpg", caption="Eyes", use_column_width=True)
    st.write("Let NoVA-Scan detect your eye region automatically for a clear and accurate image.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.image("https://i.imgur.com/r7p1u1J.jpg", caption="Palm", use_column_width=True)
    st.write("Your palm area is identified instantly, helping the AI prepare it for detailed analysis.")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.image("https://i.imgur.com/UpXVoZw.jpg", caption="Nail Beds", use_column_width=True)
    st.write("NoVA-Scan pinpoints your nail area so the system can focus on the right details.")
    st.markdown("</div>", unsafe_allow_html=True)

# ======== HOW IT WORKS ========
st.markdown("<div class='section center'><h2>⚙️ How It Works</h2></div>", unsafe_allow_html=True)

cols = st.columns(3)
steps = [
    ("1️⃣ Capture or Upload", "Take a photo or upload an image showing your eyes, palm, or nail beds."),
    ("2️⃣ AI Detection", "NoVA-Scan uses advanced YOLO object detection to locate the key regions."),
    ("3️⃣ Review Results", "View detected areas and confirm accuracy before saving or moving on.")
]
for i, (title, desc) in enumerate(steps):
    with cols[i]:
        st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

# ======== START BUTTON ========
st.markdown("<div class='center' style='margin-top:2rem;'>", unsafe_allow_html=True)
if st.button("🚀 START NoVA-SCAN"):
    st.session_state["show_scan"] = True
st.markdown("</div>", unsafe_allow_html=True)

# ======== SCAN SECTION ========
if st.session_state.get("show_scan"):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("🔍 Run AI Detection")

    option = st.selectbox("Choose Detection Type:", ["Eyes", "Palm", "Nails"])
    file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    def run_model(script, image_path, save_dir):
        result = subprocess.run(["python", script, image_path, str(save_dir)], capture_output=True, text=True)
        try:
            detections = json.loads(result.stdout)
            return detections
        except json.JSONDecodeError:
            st.error("Model output not valid JSON.")
            st.text(result.stdout)
            return None

    if file:
        image_path = OUTPUT_DIR / f"{option.lower()}_input.png"
        with open(image_path, "wb") as f:
            f.write(file.getbuffer())

        if st.button(f"Run {option} Detection"):
            script_map = {
                "Eyes": "nova_eye.py",
                "Palm": "finalpalm.py",
                "Nails": "nova_nail.py"
            }
            save_dir = OUTPUT_DIR / option.lower()
            save_dir.mkdir(exist_ok=True)
            with st.spinner("Running model..."):
                results = run_model(script_map[option], str(image_path), save_dir)
            if results:
                st.image(results["annotated_image"], caption=f"{option} Detection Result")
                st.json(results)

st.markdown("<p class='center' style='margin-top:3rem;'>See. Scan. Detect. — the NoVA way.</p>", unsafe_allow_html=True)
