# app.py
import streamlit as st
import os
import tempfile
from nova_eye import main as process_image

st.set_page_config(page_title="NOVA Eye Detection", layout="centered")

st.title("NOVA Eye Detection Pipeline")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    output_dir = "output/eye"
    result = process_image(tmp_path, output_dir)

    if "error" in result:
        st.error(result["error"])
    else:
        st.image(result["annotated_image"], caption="Annotated Image", use_column_width=True)
        st.write(f"Detected Eyes: {result['num_eyes']}")

        # Download zip of crops
        with open(result["zip_file"], "rb") as f:
            st.download_button(
                label="Download Eye Crops",
                data=f,
                file_name="eye_crops.zip",
                mime="application/zip"
            )
