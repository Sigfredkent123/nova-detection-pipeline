# main_pipeline.py
# -*- coding: utf-8 -*-

import subprocess, json, cv2, os
from pathlib import Path
from tkinter import Tk, filedialog

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def pick_image(title="Select an image"):
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title=title, filetypes=[("Images", "*.jpg *.png *.jpeg")])
    root.destroy()
    return path

def run_model(script, image_path, save_dir):
    """Run a model and capture its JSON output."""
    print(f"\n Running {script} on {image_path}...")
    result = subprocess.run(
        ["python", script, image_path, str(save_dir)],
        capture_output=True, text=True
    )
    try:
        detections = json.loads(result.stdout)
        return detections
    except json.JSONDecodeError:
        print(" Could not parse JSON from output.")
        print(result.stdout)
        return None

def display_crops(title, image_paths):
    """Show cropped images briefly in OpenCV window."""
    if not image_paths:
        print(f" No extracted {title.lower()} regions.")
        return
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            cv2.imshow(f"{title} - {Path(path).name}", img)
            cv2.waitKey(1000)
    cv2.destroyAllWindows()

def main():
    print("===  EYE / LOWER CONJUNCTIVA DETECTION ===")
    eye_path = pick_image("Select Eye / Conjunctiva Image")
    eye_dir = OUTPUT_DIR / "eye"
    eye_dir.mkdir(exist_ok=True)
    eye_results = run_model("nova_eye.py", eye_path, eye_dir)
    display_crops("Eye / Conjunctiva", eye_results.get("saved_eyes", []) if eye_results else [])

    print("\n===  PALM DETECTION ===")
    palm_path = pick_image("Select Palm Image")
    palm_dir = OUTPUT_DIR / "palm"
    palm_dir.mkdir(exist_ok=True)
    palm_results = run_model("finalpalm.py", palm_path, palm_dir)
    display_crops("Palm", palm_results.get("saved_palms", []) if palm_results else [])

    print("\n===  NAIL DETECTION ===")
    nail_path = pick_image("Select Nail Image")
    nail_dir = OUTPUT_DIR / "nail"
    nail_dir.mkdir(exist_ok=True)
    nail_results = run_model("nova_nail.py", nail_path, nail_dir)
    display_crops("Nail", nail_results.get("saved_nails", []) if nail_results else [])

    combined = {
        "eye_results": eye_results,
        "palm_results": palm_results,
        "nail_results": nail_results
    }
    combined_path = OUTPUT_DIR / "combined_results.json"
    with open(combined_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n All detections complete! Results saved in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()
 