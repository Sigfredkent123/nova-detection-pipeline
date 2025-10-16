# nova_eye.py
# -*- coding: utf-8 -*-
"""
NOVA Eye Detection - Streamlit Cloud Compatible
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow
from inference_sdk import InferenceAPIClient
import streamlit as st


def extract_predictions(result):
    """
    Safely extract the list of predictions from workflow result.
    Handles both list and dict structures returned by inference-sdk 0.58.1.
    """
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
    else:
        first = result

    if isinstance(first, dict):
        preds = first.get("predictions", [])
        if isinstance(preds, dict) and "predictions" in preds:
            return preds["predictions"]
        elif isinstance(preds, list):
            return preds
    return []


def detect_eyes(image_path, output_dir="output/eye"):
    """
    Detect eyes using Roboflow workflow, annotate image, save crops, and return metadata.
    Compatible with inference-sdk==0.58.1
    """
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    # Get Roboflow API key from Streamlit secrets
    api_key = st.secrets.get("roboflow_api_key")
    if not api_key:
        raise ValueError("Roboflow API key not found in st.secrets!")

    client = InferenceAPIClient(api_key)

    # Run workflow (images as list for this SDK version)
    result = client.run_workflow(
        workspace_name="newnova-mkn50",
        workflow_id="custom-workflow-2",
        images=[image_path]
    )

    # Extract predictions safely
    predictions = extract_predictions(result)

    # Annotate image
    annotated_path = os.path.join(output_dir, f"annotated_{os.path.basename(image_path)}")
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for pred in predictions:
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        cls = pred.get("class", "eye")
        conf = pred.get("confidence", 1)
        x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
        draw.text((x0, y0 - 10), f"{cls} {conf:.2f}", fill="red", font=font)

    image.save(annotated_path)

    # Save crops
    crop_dir = os.path.join(output_dir, "crops")
    os.makedirs(crop_dir, exist_ok=True)
    orig = Image.open(image_path).convert("RGB")
    saved_crops = []

    for i, pred in enumerate(predictions):
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        cls = pred.get("class", "eye")
        x0, y0, x1, y1 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
        crop = orig.crop((x0, y0, x1, y1))
        crop_path = os.path.join(crop_dir, f"crop_{i}_{cls}.png")
        crop.save(crop_path)
        saved_crops.append(crop_path)

    # Zip crops
    zip_filename = os.path.join(output_dir, "eye_crops.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk(crop_dir):
            for file in files:
                zipf.write(os.path.join(root, file))

    return {
        "image": image_path,
        "annotated_image": annotated_path,
        "num_eyes": len(predictions),
        "saved_eyes": saved_crops,
        "zip_file": zip_filename,
        "predictions": predictions
    }
