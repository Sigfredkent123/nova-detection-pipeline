# app.py
import os
import streamlit as st
from nova_eye import detect_eyes
from PIL import Image

st.set_page_config(page_title="NOVA Eye Detection", layout="centered")

st.title("NOVA Eye Detection Pipeline")
st.write("Upload an image, and the model will detect eyes, annotate, and save crops.")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Save uploaded image temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Processing image...")
    result = detect_eyes(temp_path)

    if "error" in result:
        st.error(result["error"])
    else:
        st.success(f"Detected {result['num_eyes']} eyes!")

        # Show annotated image
        st.image(result["annotated_image"], caption="Annotated Image", use_column_width=True)

        # Download zip of cropped eyes
        with open(result["zip_file"], "rb") as f:
            st.download_button(
                label="Download Cropped Eyes ZIP",
                data=f,
                file_name="eye_crops.zip",
                mime="application/zip"
            )
