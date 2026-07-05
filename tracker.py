from ultralytics import YOLO
import cv2
import supervision as sv
import sys
import subprocess as sp  # for ffmpeg re-encoding
import json
print("Step 1: starting, about to load YOLO model", flush=True)
video_path = sys.argv[1]
job_id = sys.argv[2]  # unique ID for this specific upload, passed in by app.py
model = YOLO("yolov8n.pt")
print("Step 2: YOLO model loaded successfully", flush=True)
cap = cv2.VideoCapture(video_path)
print("Step 3: video capture opened", flush=True)
# Output Video Setup — filenames now include job_id so concurrent
# uploads never overwrite each other's files.
raw_output_path = f"static/output_raw_{job_id}.mp4"
final_output_path = f"static/output_{job_id}.mp4"
progress_path = f"static/progress_{job_id}.json"
report_path = f"tracking_report_{job_id}.txt"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(raw_output_path, fourcc, fps, (width, height))
tracker = sv.ByteTrack()
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()
car_count = 0
track_frames = {}
object_time = {}
max_objects = 0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_num = 0
vehicle_type = {}
print("Step 4: entering frame processing loop", flush=True)
while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_num += 1

    # Write progress percentage to THIS job's own progress file
    if total_frames > 0:
        progress = int((frame_num / total_frames) * 100)
        with open(progress_path, "w") as pf:
            json.dump({"progress": progress, "done": False}, pf)

    results = model(frame, verbose=False)[0]

    detections = sv.Detections.from_ultralytics(results)

    vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    mask = [cls in vehicle_classes for cls in detections.class_id]
    detections = detections[mask]

    detections = tracker.update_with_detections(detections)

    if detections.tracker_id is not None:

        for tracker_id in detections.tracker_id:

            if tracker_id not in track_frames:
                track_frames[tracker_id] = 1
            else:
                track_frames[tracker_id] += 1

            if track_frames[tracker_id] == 10:
                car_count += 1

    if detections.tracker_id is not None:

        current_ids = detections.tracker_id

        for tracker_id, class_id in zip(detections.tracker_id, detections.class_id):

            if tracker_id not in object_time:
                object_time[tracker_id] = 0
                vehicle_type[tracker_id] = class_id

            object_time[tracker_id] += 1

        max_objects = max(max_objects, len(current_ids))

    labels = [
        f"ID {tracker_id}"
        for tracker_id in detections.tracker_id
    ]

    annotated_frame = box_annotator.annotate(
        scene=frame,
        detections=detections
    )

    annotated_frame = label_annotator.annotate(
        scene=annotated_frame,
        detections=detections,
        labels=labels
    )

    annotated_frame = trace_annotator.annotate(
        scene=annotated_frame,
        detections=detections
    )

    cv2.putText(
        annotated_frame,
        f"Total Vehicles: {car_count}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    out.write(annotated_frame)

with open(report_path, "w") as f:

    f.write("Tracking Report\n")
    f.write("---------------------------\n")

    f.write(f"Unique Vehicles: {car_count}\n")

    f.write(f"Max Simultaneous Objects: {max_objects}\n\n")

    class_names = {2: "Cars", 3: "Motorcycles", 5: "Buses", 7: "Trucks"}
    type_counts = {name: 0 for name in class_names.values()}

    for tid, cid in vehicle_type.items():
        if track_frames.get(tid, 0) >= 10:
            name = class_names.get(cid, "Unknown")
            type_counts[name] += 1

    f.write("Vehicle Type Breakdown\n")
    f.write("---------------------------\n")
    for name, count in type_counts.items():
        f.write(f"{name}: {count}\n")

    f.write("\nTime in Frame Per Object\n")
    f.write("---------------------------\n")

    for obj_id, frames in object_time.items():

        seconds = frames / fps
        f.write(f"ID {obj_id}: {seconds:.2f} seconds\n")

out.release()
cap.release()
cv2.destroyAllWindows()

# Re-encode to H.264 (libx264) so browser can play it
sp.run([
    "ffmpeg", "-y",
    "-i", raw_output_path,
    "-vcodec", "libx264",
    "-pix_fmt", "yuv420p",
    final_output_path
])

# Mark progress as done, on THIS job's own progress file
with open(progress_path, "w") as pf:
    json.dump({"progress": 100, "done": True}, pf)