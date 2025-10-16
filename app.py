import streamlit as st
from pathlib import Path
from nova_eye import detect_eyes
import json

st.set_page_config(page_title="NOVA Eye Detection", layout="wide")
st.title("👁️ NOVA Eye Detection")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save to temp location
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    image_path = temp_dir / uploaded_file.name
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.image(str(image_path), caption="Uploaded Image", use_column_width=True)

    # Run detection
    st.info("Detecting eyes...")
    try:
        result = detect_eyes(str(image_path))

        # 🔹 DEBUG: show raw Roboflow result in app
        st.subheader("Raw result from Roboflow")
        st.text(json.dumps(result, indent=2, ensure_ascii=False))

        # Handle predictions safely
        # Some Roboflow workflows return a list of dicts instead of dict
        if isinstance(result, list):
            # Take predictions from the first item if it's a list
            predictions = result[0].get("predictions", []) if result else []
        else:
            predictions = result.get("predictions", [])

        st.success(f"✅ Detected {len(predictions)} eyes!")

        # Show annotated image
        st.image(result["annotated_image"], caption="Annotated Image", use_column_width=True)

        # Show cropped eyes
        st.subheader("Cropped Eyes")
        for crop in result["saved_eyes"]:
            st.image(crop, width=150)

        # Provide ZIP download
        with open(result["zip_file"], "rb") as f:
            st.download_button("Download all crops as ZIP", f, file_name="eye_crops.zip")

    except Exception as e:
        st.error(f"Error: {e}")
