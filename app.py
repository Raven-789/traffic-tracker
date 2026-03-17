from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json
 
app = Flask(__name__)
 
UPLOAD_FOLDER = "uploads"       #creates a folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
 
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
 
 
@app.route("/", methods=["GET", "POST"])
def index():
 
    video_path = None
    result_video = None
    report_text = None
 
    if request.method == "POST":
 
        file = request.files["video"]
 
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
 
        file.save(filepath)
 
        # ✅ Reset progress before starting
        with open("static/progress.json", "w") as pf:
            json.dump({"progress": 0, "done": False}, pf)
 
        # Run tracker
        subprocess.run(["python", "tracker.py", filepath])
 
        video_path = filepath
        result_video = "static/output.mp4"
 
        with open("tracking_report.txt", "r") as f:
            report_text = f.read()
 
    return render_template(
        "index.html",
        video_path=video_path,
        result_video=result_video,
        report_text=report_text
    )
 
 
# ✅ Progress route — browser polls this while processing
@app.route("/progress")
def progress():
    try:
        with open("static/progress.json", "r") as pf:
            data = json.load(pf)
        return jsonify(data)
    except:
        return jsonify({"progress": 0, "done": False})
 
 
if __name__ == "__main__":
    app.run(debug=True)