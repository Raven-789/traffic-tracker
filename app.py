from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
import threading
import uuid
import sys
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def run_tracker(filepath, job_id):
    # Runs in a separate thread. This does NOT block Flask from
    # answering other requests (like /progress) while it works.
    subprocess.run([sys.executable, "tracker.py", filepath, job_id])


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File too large. Please upload a video under 100MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")

    if file is None or file.filename == "":
        return jsonify({"error": "No file was selected. Please choose a video to upload."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a .mp4, .mov, .avi, or .mkv file."}), 400

    # A random, unique ID for this specific upload — used to keep
    # every user's files separate from everyone else's.
    job_id = uuid.uuid4().hex

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{job_id}_{secure_filename(file.filename)}")
    file.save(filepath)

    # Create this job's own progress file
    with open(f"static/progress_{job_id}.json", "w") as pf:
        json.dump({"progress": 0, "done": False}, pf)

    # Start processing in the background. This line returns immediately —
    # it does NOT wait for the video to finish.
    thread = threading.Thread(target=run_tracker, args=(filepath, job_id))
    thread.start()

    return jsonify({"status": "started", "job_id": job_id})


@app.route("/progress")
def progress():
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"progress": 0, "done": False})
    try:
        with open(f"static/progress_{job_id}.json", "r") as pf:
            data = json.load(pf)
        return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"progress": 0, "done": False})

@app.route("/result")
def result():
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "Missing job_id"}), 400
    try:
        with open(f"tracking_report_{job_id}.txt", "r") as f:
            report_text = f.read()
    except FileNotFoundError:
        report_text = ""
    return jsonify({
        "result_video": f"static/output_{job_id}.mp4",
        "report_text": report_text
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)