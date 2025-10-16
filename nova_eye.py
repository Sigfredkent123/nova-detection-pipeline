# nova_eye.py
# -*- coding: utf-8 -*-
"""
NOVA Eye Detection - Streamlit / GUI Compatible
"""

import os
import sys
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageTk
from inference_sdk import InferenceHTTPClient

# Optional GUI dependencies
import tkinter as tk
from tkinter import filedialog, messagebox, Label


def detect_eyes(image_path, output_dir="output/eye"):
    """
    Detect eyes using Roboflow workflow,
    annotate image, save crops, and return metadata.
    """
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="rXklt59qJc3uGQUVi7iZ"
    )

    # Run workflow
    result = client.run_workflow(
        workspace_name="newnova-mkn50",
        workflow_id="custom-workflow-2",
        images={"image": image_path},
        use_cache=True
    )

    # Extract predictions correctly
    predictions = result[0]["predictions"]["predictions"] if result else []

    # Annotate image
    annotated_path = os.path.join(output_dir, f"annotated_{os.path.basename(image_path)}")
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for pred in predictions:
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        cls = pred["class"]
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
        cls = pred["class"]
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

    # Return metadata
    return {
        "image": image_path,
        "annotated_image": annotated_path,
        "num_eyes": len(predictions),
        "saved_eyes": saved_crops,
        "zip_file": zip_filename,
        "predictions": predictions
    }


# ---------------------------
# Simple Local GUI (Tkinter)
# ---------------------------
def launch_gui():
    def select_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not file_path:
            return
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)

    def run_detection():
        img_path = entry_path.get()
        if not img_path:
            messagebox.showwarning("No file", "Please select an image file first.")
            return

        try:
            lbl_status.config(text="Detecting eyes...", fg="blue")
            root.update()

            result = detect_eyes(img_path)
            annotated_path = result["annotated_image"]

            lbl_status.config(text=f"Detected {result['num_eyes']} eyes!", fg="green")

            # Show annotated image
            img = Image.open(annotated_path)
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            lbl_image.config(image=img_tk)
            lbl_image.image = img_tk  # prevent GC

        except Exception as e:
            messagebox.showerror("Error", str(e))
            lbl_status.config(text="Detection failed", fg="red")

    # Tkinter GUI setup
    root = tk.Tk()
    root.title("NOVA Eye Detection")
    root.geometry("500x600")

    tk.Label(root, text="Select an image to detect eyes:", font=("Arial", 12)).pack(pady=10)

    entry_path = tk.Entry(root, width=50)
    entry_path.pack(pady=5)

    tk.Button(root, text="Browse", command=select_file).pack(pady=5)
    tk.Button(root, text="Run Detection", command=run_detection, bg="green", fg="white").pack(pady=10)

    lbl_status = tk.Label(root, text="", font=("Arial", 12))
    lbl_status.pack(pady=5)

    lbl_image = Label(root)
    lbl_image.pack(pady=10)

    root.mainloop()


# ---------------------------
# CLI Mode
# ---------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Run GUI if no arguments
        launch_gui()
    elif len(sys.argv) >= 2:
        image_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/eye"
        try:
            result = detect_eyes(image_path, output_dir)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
