import base64
import io
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from api.endpoints import router as api_router
from api.roi import router as roi_router, set_roi
from services.face_detector import get_detector
from utils.draw import draw_roi
from db.models import init_db, save_roi

session_id = str(uuid.uuid4())[:8]
frame_counter = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

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

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_roi(self, roi_data: dict):
        self.latest_roi = roi_data
        for conn in self.active_connections:
            try:
                await conn.send_json(roi_data)
            except:
                pass

manager = ConnectionManager()
detector = get_detector()

@app.get("/")
def root():
    return {"status": "ok", "message": "LookLive API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            image = Image.open(io.BytesIO(data))
            
            bbox = detector.detect_face(image)
            processed = draw_roi(image, bbox)
            
            buf = io.BytesIO()
            processed.save(buf, format='JPEG', quality=75)
            frame_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            response = {
                "roi": bbox,
                "frame": frame_b64
            }
            await websocket.send_json(response)
            
            if bbox:
                await manager.broadcast_roi({"roi": bbox})
                set_roi(bbox)
                global frame_counter
                frame_counter += 1
                save_roi(session_id, frame_counter, bbox)
    except WebSocketDisconnect:
        manager.disconnect(websocket)