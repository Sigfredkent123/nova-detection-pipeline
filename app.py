import os
import subprocess
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# === Flask Setup ===
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["OUTPUT_FOLDER"] = "static/outputs"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# === Allowed Extensions ===
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route("/analyze", methods=["POST"])
def analyze_image():
    parameter = request.form.get("parameter")
    file = request.files.get("file")

    if not file or file.filename == "":
        return render_template("results.html", error="No file uploaded")

    if not allowed_file(file.filename):
        return render_template("results.html", error="Invalid file type")

    # === Save Uploaded File ===
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # === Choose Which Detection Script to Run ===
    if parameter == "eye":
        script = "nova_eye.py"
    elif parameter == "palm":
        script = "finalpalm.py"
    elif parameter == "nailbed":
        script = "nova_nail.py"
    else:
        return render_template("results.html", error="Invalid detection type")

    # === Run the Detection Script ===
    try:
        result = subprocess.run(
            ["python3", script, input_path],
            capture_output=True,
            text=True,
            check=True
        )
        output_data = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return render_template("results.html", error=f"Error running {script}: {e.stderr}")
    except json.JSONDecodeError:
        return render_template("results.html", error="Failed to parse model output")

    # === Prepare Image URLs for HTML ===
    annotated_image = f"/{output_data.get('annotated_image', '')}"
    original_image = f"/{input_path}"

    # === Count Detections ===
    num_objects = (
        output_data.get("num_eyes")
        or output_data.get("num_palms")
        or output_data.get("num_nails")
        or 0
    )

    # === Render Results Page ===
    return render_template(
        "results.html",
        parameter=parameter.capitalize(),
        annotated_image=annotated_image,
        original_image=original_image,
        num_objects=num_objects,
    )

# === Run Flask App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
