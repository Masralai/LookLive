import numpy as np
from PIL import Image
from mtcnn import MTCNN


class FaceDetector:
    _instance = None

    def __init__(self):
        self.detector = MTCNN()

    def detect_face(self, image: Image.Image):
        """Detect face in PIL Image, return bounding box or None"""
        if image is None:
            return None

        frame_rgb = np.array(image.convert('RGB'))
        results = self.detector.detect_faces(frame_rgb)

        if not results:
            return None

        # Get first face (PRD: single face assumption)
        face = results[0]
        box = face['box']

        return {
            'x': int(box[0]),
            'y': int(box[1]),
            'w': int(box[2]),
            'h': int(box[3]),
            'confidence': float(face['confidence'])
        }


def get_detector():
    """Get singleton FaceDetector instance"""
    if FaceDetector._instance is None:
        FaceDetector._instance = FaceDetector()
    return FaceDetector._instance