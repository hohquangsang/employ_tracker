from ultralytics import YOLO

class YOLOPersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect_person(self, frame):
        results = self.model(frame)[0]
        people = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, cls_id = r
            if int(cls_id) == 0:  # class 0 là person
                people.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "center": (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                    "confidence": score
                })
        return people
