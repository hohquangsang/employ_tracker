import cv2
import torch
import json
import numpy as np
from ultralytics import YOLO
import config
import os
from database import log_action

def load_zones():
    try:
        with open("zones.json") as f:
            data = json.load(f)
            return [np.array(v, dtype=np.int32) for v in data.values()], list(data.keys())
    except:
        return [], []

time_in_area = {}
entry_time = {}
frame_duration = 1 / 30
frame_count = 0

def generate_frames():
    global frame_count

    if not config.CURRENT_VIDEO_PATH or not os.path.exists(config.CURRENT_VIDEO_PATH):
        print("⚠️ Chưa có video nào để phát.")
        return

    cap = cv2.VideoCapture(config.CURRENT_VIDEO_PATH)
    model = YOLO("yolov8n.pt")
    model.to('cpu')

    zones, _ = load_zones()
    num_zones = len(zones)
    for i in range(num_zones):
        time_in_area[i] = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        results = model.track(frame, persist=True, classes=[0], conf=0.3, iou=0.3)
        boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes.xyxy is not None else []
        ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else []

        for box, yolo_id in zip(boxes, ids):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            matched_cabin = None

            for idx, polygon in enumerate(zones):
                if cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0:
                    matched_cabin = idx
                    break

            if matched_cabin is not None:
                status = "Đang làm việc"
                color = (0, 255, 0)  # Xanh
            else:
                status = "Không làm việc"
                color = (0, 0, 255)  # Đỏ

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, status, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def process_video(input_path, output_path):
    model = YOLO("yolov8n.pt")
    model.to('cpu')

    cap = cv2.VideoCapture(input_path)
    zones, _ = load_zones()
    num_zones = len(zones)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30,
                          (int(cap.get(3)), int(cap.get(4))))

    global frame_count
    frame_count = 0
    cabin_to_id = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        results = model.track(frame, persist=True, classes=[0], conf=0.3, iou=0.3)
        boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes.xyxy is not None else []
        ids = results[0].boxes.id.cpu().numpy() if results[0].boxes.id is not None else []

        cabin_has_person = set()

        for box, yolo_id in zip(boxes, ids):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            matched_cabin = None

            for idx, polygon in enumerate(zones):
                if cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0:
                    matched_cabin = idx
                    break

            if matched_cabin is not None:
                status = "Đang làm việc"
                color = (0, 255, 0)
                cabin_has_person.add(matched_cabin)
                if matched_cabin not in cabin_to_id:
                    cabin_to_id[matched_cabin] = matched_cabin + 1
            else:
                status = "Không làm việc"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, status, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        out.write(frame)

    cap.release()
    out.release()

    # Ghi trạng thái
    for idx in range(num_zones):
        if idx in cabin_to_id:
            log_action(str(cabin_to_id[idx]), "Dang lam")
        else:
            log_action("None", "Roi khoi noi lam viec")
