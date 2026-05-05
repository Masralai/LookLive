import numpy as np
from PIL import Image
from ultralytics import YOLO


class FaceDetector:
    _instance = None
    _model = None

    def __init__(self):
        if FaceDetector._model is None:
            FaceDetector._model = YOLO('yolov8n.pt')

    def detect_face(self, image: Image.Image):
        """Detect person in PIL Image using YOLO, return bounding box or None"""
        if image is None:
            return None

        frame_rgb = np.array(image.convert('RGB'))
        results = self._model(frame_rgb, verbose=False, device=0)[0]

        boxes = results.boxes
        if boxes is None or len(boxes) == 0:
            return None

        best_box = None
        best_conf = 0.0
        for box in boxes:
            cls = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())
            if cls == 0 and conf > best_conf:
                best_conf = conf
                best_box = box

        if best_box is None:
            return None

        box = best_box.xyxy[0].cpu().numpy()

        return {
            'x': int(box[0]),
            'y': int(box[1]),
            'w': int(box[2] - box[0]),
            'h': int(box[3] - box[1]),
            'confidence': best_conf
        }


def get_detector():
    """Get singleton FaceDetector instance"""
    if FaceDetector._instance is None:
        FaceDetector._instance = FaceDetector()
    return FaceDetector._instance