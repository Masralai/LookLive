from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import base64
from services.face_detector import get_detector
from utils.draw import draw_roi

router = APIRouter()

@router.post("/video/ingest")
async def ingest_frame(file: UploadFile = File(...)):
    """Receive video frame, detect face, draw ROI, return processed frame"""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        detector = get_detector()
        bbox = detector.detect_face(image)
        
        processed = draw_roi(image, bbox)
        
        buf = io.BytesIO()
        processed.save(buf, format='JPEG', quality=85)
        encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return {
            "status": "ok",
            "roi": bbox,
            "frame": encoded
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))