import base64
import io
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from api.endpoints import router as api_router
from api.roi import router as roi_router, set_roi
from services.face_detector import get_detector
from utils.draw import draw_roi
from db.models import init_db, save_roi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session_id = str(uuid.uuid4())[:8]
frame_counter = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LookLive API...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down LookLive API...")

app = FastAPI(title="LookLive Face Detection API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(roi_router, prefix="/api", tags=["roi"])

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.latest_roi = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast_roi(self, roi_data: dict):
        self.latest_roi = roi_data
        for conn in self.active_connections:
            try:
                await conn.send_json(roi_data)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

manager = ConnectionManager()
detector = get_detector()

@app.get("/")
def root():
    return {"status": "ok", "message": "LookLive API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    await manager.connect(websocket)
    frame_num = 0
    
    try:
        while True:
            try:
                data = await websocket.receive_bytes()
                frame_num += 1
                
                # Try to open as image
                try:
                    image = Image.open(io.BytesIO(data))
                    image = image.convert("RGB")  # Ensure RGB
                except Exception as e:
                    logger.warning(f"Invalid image data: {e}")
                    await websocket.send_json({"error": "Invalid image data", "frame": None})
                    continue
                
                # Detect face
                bbox = detector.detect_face(image)
                
                # Draw ROI (always returns an image, even if no face)
                processed = draw_roi(image, bbox)
                
                # Encode the processed frame
                buf = io.BytesIO()
                processed.save(buf, format='JPEG', quality=75)
                frame_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                
                response = {
                    "roi": bbox,
                    "frame": frame_b64,
                    "frame_id": frame_num
                }
                await websocket.send_json(response)
                
                # Save ROI if face detected
                if bbox:
                    await manager.broadcast_roi({"roi": bbox})
                    set_roi(bbox)
                    global frame_counter
                    frame_counter += 1
                    save_roi(session_id, frame_counter, bbox)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Frame processing error: {e}")
                try:
                    await websocket.send_json({"error": str(e)})
                except:
                    break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)