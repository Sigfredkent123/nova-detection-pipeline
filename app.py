# app.py
# -*- coding: utf-8 -*-
"""
Streamlit app for NOVA Eye Detection
"""

import streamlit as st
from nova_eye import detect_eyes
from PIL import Image
import os

st.set_page_config(page_title="NOVA Eye Detection", layout="centered")

st.title("👁 NOVA Eye Detection")
st.write("Upload an image, and the app will detect eyes and provide annotated results.")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save uploaded image temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    image_path = os.path.join(temp_dir, uploaded_file.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(image_path, caption="Uploaded Image", use_column_width=True)

    if st.button("Run Eye Detection"):
        try:
            with st.spinner("Detecting eyes..."):
                output_dir = "output_streamlit"
                result = detect_eyes(image_path, output_dir)

            st.success(f"✅ Detected {result['num_eyes']} eyes!")

            # Display annotated image
            annotated_image = Image.open(result["annotated_image"])
            st.image(annotated_image, caption="Annotated Image", use_column_width=True)

            # Display cropped eyes
            st.write("Cropped Eyes:")
            for crop_path in result["saved_eyes"]:
                crop_img = Image.open(crop_path)
                st.image(crop_img, width=150)

            # Provide ZIP download
            with open(result["zip_file"], "rb") as f:
                st.download_button(
                    label="Download Crops as ZIP",
                    data=f,
                    file_name="eye_crops.zip",
                    mime="application/zip"
                )

        except Exception as e:
            st.error(f"Error: {e}")
