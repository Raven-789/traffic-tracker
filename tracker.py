






# #  --------------------6th Version (Above)---------------------------------------------------------------------6th Version(Above)-----------



# from ultralytics import YOLO
# import cv2
# import supervision as sv
# import sys
# import subprocess as sp  # ✅ for ffmpeg re-encoding
# import json

# video_path = sys.argv[1]

# # -------------------------
# # 1️⃣ Load Model
# # -------------------------

# model = YOLO("yolov8n.pt")

# cap = cv2.VideoCapture(video_path)

# # -------------------------
# # Output Video Setup
# # -------------------------

# output_path = "static/output_raw.mp4"

# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# fps = cap.get(cv2.CAP_PROP_FPS)

# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# tracker = sv.ByteTrack()

# box_annotator = sv.BoxAnnotator()
# label_annotator = sv.LabelAnnotator()
# trace_annotator = sv.TraceAnnotator()

# # -----------------------------------------------------------------------------------------------------------------------------
# # 2️⃣ Car Counter Setup
# # -----------------------------------------------------------------------------------------------------------------------------

# car_count = 0
# track_frames = {}

# # -------------------------
# # 3️⃣ Analytics Setup
# # -------------------------

# object_time = {}
# max_objects = 0
# # fps = cap.get(cv2.CAP_PROP_FPS)  #Don't need it

# # ✅ Get total frame count for progress tracking
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# frame_num = 0
# vehicle_type = {} 
# # -------------------------
# # 4️⃣ Main Loop
# # -------------------------

# while True:

#     ret, frame = cap.read()

#     if not ret:
#         break

#     frame_num += 1

#     # ✅ Write progress percentage to file so Flask can read it
#     if total_frames > 0:
#         progress = int((frame_num / total_frames) * 100)
#         with open("static/progress.json", "w") as pf:
#             json.dump({"progress": progress}, pf)

#     # Run YOLO detection
#     results = model(frame, verbose=False)[0]

#     # Convert detections
#     detections = sv.Detections.from_ultralytics(results)

#     # -------------------------
#     # Keep Only Vehicles
#     # -------------------------

#     vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
#     mask = [cls in vehicle_classes for cls in detections.class_id]
#     detections = detections[mask]

#     # Track objects
#     detections = tracker.update_with_detections(detections)

#     # -----------------------------------------------------------------------------------------------------------------------------
#     # Stable Counting
#     # -----------------------------------------------------------------------------------------------------------------------------

#     if detections.tracker_id is not None:

#         for tracker_id in detections.tracker_id:

#             if tracker_id not in track_frames:
#                 track_frames[tracker_id] = 1
#             else:
#                 track_frames[tracker_id] += 1

#             if track_frames[tracker_id] == 10:
#                 car_count += 1

#     # -----------------------------------------------------------------------------------------------------------------------------
#     # Time-in-frame tracking
#     # -----------------------------------------------------------------------------------------------------------------------------

#     if detections.tracker_id is not None:

#         current_ids = detections.tracker_id

#         for tracker_id in current_ids:

#             if tracker_id not in object_time:
#                 object_time[tracker_id] = 0
                

#             object_time[tracker_id] += 1

#         max_objects = max(max_objects, len(current_ids))

#     # Create labels
#     labels = [
#         f"ID {tracker_id}"
#         for tracker_id in detections.tracker_id
#     ]

#     # Draw bounding boxes
#     annotated_frame = box_annotator.annotate(
#         scene=frame,
#         detections=detections
#     )

#     # Draw labels
#     annotated_frame = label_annotator.annotate(
#         scene=annotated_frame,
#         detections=detections,
#         labels=labels
#     )

#     # Draw motion trails
#     annotated_frame = trace_annotator.annotate(
#         scene=annotated_frame,
#         detections=detections
#     )

#     # -------------------------
#     # Display Counter
#     # -------------------------

#     cv2.putText(
#         annotated_frame,
#         # for stable count----------------------------------------------
#         f"Total Vehicles: {car_count}",
#         # for frame by frame count-------------------------------------
#         # f"Total Vehicles: {len(object_time)}",

#         (50,50),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         1,      #Fonst scale
#         (0,255,0),
#         3       #thickness
#     )

#     # save processed frame
#     out.write(annotated_frame)

#     # Show frame
#     # cv2.imshow("Traffic Analytics", annotated_frame)

# # -------------------------
# # 5️⃣ Generate Text Report
# # -------------------------

# with open("tracking_report.txt", "w") as f:

#     f.write("Tracking Report\n")
#     f.write("---------------------------\n")

#     # this for exact frame tracking even if the obj dissaperas
#     # f.write(f"Unique Objects: {len(object_time)}\n")
#     # if you don't want frame by frame count
#     f.write(f"Unique Vehicles: {car_count}\n")

#     f.write(f"Max Simultaneous Objects: {max_objects}\n\n")

#     f.write("Time in Frame Per Object\n")

#     for obj_id, frames in object_time.items():

#         seconds = frames / fps
#         f.write(f"ID {obj_id}: {seconds:.2f} seconds\n")

# out.release()
# cap.release()
# cv2.destroyAllWindows()

# # ✅ Re-encode to H.264 (libx264) so browser can play it
# sp.run([
#     "ffmpeg", "-y",
#     "-i", "static/output_raw.mp4",
#     "-vcodec", "libx264",
#     "-pix_fmt", "yuv420p",
#     "static/output.mp4"
# ])

# # ✅ Mark progress as done
# with open("static/progress.json", "w") as pf:
#     json.dump({"progress": 100, "done": True}, pf)







































from ultralytics import YOLO
import cv2
import supervision as sv
import sys
import subprocess as sp  # ✅ for ffmpeg re-encoding
import json

video_path = sys.argv[1]

# -------------------------
# 1️⃣ Load Model
# -------------------------

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(video_path)

# -------------------------
# Output Video Setup
# -------------------------

output_path = "static/output_raw.mp4"

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)  # ✅ FIX: restored fps — was commented out but still used in report

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

tracker = sv.ByteTrack()

box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()

# -----------------------------------------------------------------------------------------------------------------------------
# 2️⃣ Car Counter Setup
# -----------------------------------------------------------------------------------------------------------------------------

car_count = 0
track_frames = {}

# -------------------------
# 3️⃣ Analytics Setup
# -------------------------

object_time = {}
max_objects = 0

# ✅ Get total frame count for progress tracking
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_num = 0

vehicle_type = {}  # ✅ stores class ID per tracker ID (was declared but never filled before)

# -------------------------
# 4️⃣ Main Loop
# -------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_num += 1

    # ✅ Write progress percentage to file so Flask can read it
    if total_frames > 0:
        progress = int((frame_num / total_frames) * 100)
        with open("static/progress.json", "w") as pf:
            json.dump({"progress": progress}, pf)

    # Run YOLO detection
    results = model(frame, verbose=False)[0]

    # Convert detections
    detections = sv.Detections.from_ultralytics(results)

    # -------------------------
    # Keep Only Vehicles
    # -------------------------

    vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    mask = [cls in vehicle_classes for cls in detections.class_id]
    detections = detections[mask]

    # Track objects
    detections = tracker.update_with_detections(detections)

    # -----------------------------------------------------------------------------------------------------------------------------
    # Stable Counting
    # -----------------------------------------------------------------------------------------------------------------------------

    if detections.tracker_id is not None:

        for tracker_id in detections.tracker_id:

            if tracker_id not in track_frames:
                track_frames[tracker_id] = 1
            else:
                track_frames[tracker_id] += 1

            if track_frames[tracker_id] == 10:
                car_count += 1

    # -----------------------------------------------------------------------------------------------------------------------------
    # Time-in-frame tracking
    # -----------------------------------------------------------------------------------------------------------------------------

    if detections.tracker_id is not None:

        current_ids = detections.tracker_id

        for tracker_id, class_id in zip(detections.tracker_id, detections.class_id):  # ✅ CHANGED: added class_id alongside tracker_id

            if tracker_id not in object_time:
                object_time[tracker_id] = 0
                vehicle_type[tracker_id] = class_id  # ✅ ADDED: save vehicle type when first seen

            object_time[tracker_id] += 1

        max_objects = max(max_objects, len(current_ids))

    # Create labels
    labels = [
        f"ID {tracker_id}"
        for tracker_id in detections.tracker_id
    ]

    # Draw bounding boxes
    annotated_frame = box_annotator.annotate(
        scene=frame,
        detections=detections
    )

    # Draw labels
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame,
        detections=detections,
        labels=labels
    )

    # Draw motion trails
    annotated_frame = trace_annotator.annotate(
        scene=annotated_frame,
        detections=detections
    )

    # -------------------------
    # Display Counter
    # -------------------------

    cv2.putText(
        annotated_frame,
        # for stable count----------------------------------------------
        f"Total Vehicles: {car_count}",
        # for frame by frame count-------------------------------------
        # f"Total Vehicles: {len(object_time)}",

        (50,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,      # Font scale
        (0,255,0),
        3       # thickness
    )

    # save processed frame
    out.write(annotated_frame)

    # Show frame
    # cv2.imshow("Traffic Analytics", annotated_frame)

# -------------------------
# 5️⃣ Generate Text Report
# -------------------------

with open("tracking_report.txt", "w") as f:

    f.write("Tracking Report\n")
    f.write("---------------------------\n")

    # if you don't want frame by frame count
    f.write(f"Unique Vehicles: {car_count}\n")
    # this for exact frame tracking even if the obj disappears
    # f.write(f"Unique Objects: {len(object_time)}\n")

    f.write(f"Max Simultaneous Objects: {max_objects}\n\n")

    # ✅ ADDED: Vehicle type breakdown
    class_names = {2: "Cars", 3: "Motorcycles", 5: "Buses", 7: "Trucks"}
    type_counts = {name: 0 for name in class_names.values()}

    for tid, cid in vehicle_type.items():
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

# ✅ Re-encode to H.264 (libx264) so browser can play it
sp.run([
    "ffmpeg", "-y",
    "-i", "static/output_raw.mp4",
    "-vcodec", "libx264",
    "-pix_fmt", "yuv420p",
    "static/output.mp4"
])

# ✅ Mark progress as done
with open("static/progress.json", "w") as pf:
    json.dump({"progress": 100, "done": True}, pf)