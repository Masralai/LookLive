import mediapipe as mp
import numpy as np
from PIL import Image

class FaceDetector:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )

    def detect_face(self, image: Image.Image):
        """Detect face in PIL Image, return bounding box or None"""
        if image is None:
            return None
        
        frame_rgb = np.array(image.convert('RGB'))
        results = self.face_detector.process(frame_rgb)
        
        if not results.detections:
            return None
        
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        h, w, _ = frame_rgb.shape
        
        return {
            'x': int(bbox.xmin * w),
            'y': int(bbox.ymin * h),
            'w': int(bbox.width * w),
            'h': int(bbox.height * h),
            'confidence': float(detection.score[0])
        }


def get_detector():
    """Get singleton FaceDetector instance"""
    if not hasattr(get_detector, '_instance'):
        get_detector._instance = FaceDetector()
    return get_detector._instance