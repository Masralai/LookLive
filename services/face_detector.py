import mediapipe as mp
import numpy as np
from PIL import Image
import os

class FaceDetector:
    _instance = None
    
    def __init__(self):
        pass
    
    def _lazy_init(self):
        if FaceDetector._instance is None:
            from mediapipe.tasks.python import vision
            
            self.face_detector = vision.FaceDetector.create_from_options(
                vision.FaceDetector.Options(
                    base_options=mp.tasks.BaseOptions(
                        model_asset_path="https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_detector/float16/1/blaze_face_detector.task"
                    ),
                    running_mode=mp.tasks.vision.RunningMode.IMAGE
                )
            )

    def detect_face(self, image: Image.Image):
        """Detect face in PIL Image, return bounding box or None"""
        if image is None:
            return None
        
        if not hasattr(self, 'face_detector'):
            self._lazy_init()
        
        frame_rgb = np.array(image.convert('RGB'))
        results = self.face_detector.detect(frame_rgb)
        
        if not results.detections:
            return None
        
        detection = results.detections[0]
        bbox = detection.bounding_box
        h, w, _ = frame_rgb.shape
        
        return {
            'x': int(bbox.origin_x),
            'y': int(bbox.origin_y),
            'w': int(bbox.width),
            'h': int(bbox.height),
            'confidence': float(detection.categories[0].score) if detection.categories else 0.0
        }


def get_detector():
    """Get singleton FaceDetector instance"""
    if FaceDetector._instance is None:
        FaceDetector._instance = FaceDetector()
    return FaceDetector._instance