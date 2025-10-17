from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import subprocess
import os
import json

app = Flask(__name__)

# 🧠 ROUTES
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/camera/<parameter>')
def camera(parameter):
    return render_template('camera.html', parameter=parameter)

# ✅ Serve any local file dynamically (images, zips, etc.)
@app.route('/view/<path:filename>')
def view_file(filename):
    safe_path = os.path.normpath(filename)
    if safe_path.startswith(".."):
        return "Invalid path", 400
    return send_from_directory(os.getcwd(), safe_path)

# 🧠 Upload handler + model execution
@app.route('/analyze', methods=['POST'])
def analyze():
    parameter = request.form.get("parameter")
    image = request.files.get("image")

    if not image:
        return jsonify({"error": "No image uploaded."}), 400

    # Save uploaded image
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    image_path = os.path.join(upload_dir, image.filename)
    image.save(image_path)

    # Select model script
    scripts = {
        "eye": "nova_eye.py",
        "palm": "finalpalm.py",
        "nail": "nova_nail.py"
    }

    if parameter not in scripts:
        return jsonify({"error": f"Invalid parameter: {parameter}"}), 400

    script = scripts[parameter]
    output_dir = f"output/{parameter}"
    os.makedirs(output_dir, exist_ok=True)

    # Run the chosen model
    try:
        result = subprocess.run(
            ["python3", script, image_path, output_dir],
            capture_output=True,
            text=True,
            check=True
        )

        output = json.loads(result.stdout)
        # Add the uploaded image path for rendering
        output["original_image"] = image_path.replace("\\", "/")

        # Normalize paths for template
        for k, v in output.items():
            if isinstance(v, str):
                output[k] = v.replace("\\", "/")

        return render_template("results.html", result=output, parameter=parameter)

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Model execution failed.",
            "stderr": e.stderr
        }), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse model output."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
