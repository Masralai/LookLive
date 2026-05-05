from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import base64
import logging
from services.face_detector import get_detector
from utils.draw import draw_roi

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/video/ingest")
async def ingest_frame(file: UploadFile = File(...)):
    """Receive video frame, detect face, draw ROI, return processed frame"""
    try:
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        try:
            image = Image.open(io.BytesIO(contents))
            image = image.convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
