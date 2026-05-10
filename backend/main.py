import asyncio
import io
import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from api.endpoints import router as api_router
from api.roi import router as roi_router
from api.roi import set_roi
from db.models import init_db, save_roi
from services.face_detector import get_detector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment-based CORS
_cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in _cors_env.split(",") if origin.strip()] or ["http://localhost:3000"]
logger.info(f"CORS origins: {CORS_ORIGINS}")

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
    allow_origins=CORS_ORIGINS,
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
    import torch
    from sqlalchemy import text

    from db.models import SessionLocal

    gpu_available = torch.cuda.is_available()
    gpu_device = torch.cuda.get_device_name(0) if gpu_available else None

    db_connected = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_connected = True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")

    return {
        "status": "healthy" if db_connected else "degraded",
        "gpu": gpu_available,
        "gpu_device": gpu_device,
        "model": "loaded" if detector._model else "not_loaded",
        "model_name": "yolov8n-face.pt",
        "database": "connected" if db_connected else "disconnected"
    }

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

                # Detect face (run in thread pool to avoid blocking event loop)
                loop = asyncio.get_event_loop()
                bbox = await loop.run_in_executor(None, detector.detect_face, image)

                # Send only ROI (not frame) for real-time performance
                response = {
                    "roi": bbox,
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
                except Exception:
                    break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
