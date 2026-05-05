# LookLive Architecture

```mermaid
graph TB
    subgraph Client["Frontend (React)"]
        Cam[Webcam]
        Canvas[Canvas]
        WS[WebSocket Client]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        WS_Server[WebSocket /ws/video]
        Ingest[POST /api/video/ingest]
        Detect[MediaPipe Face Detection]
        Draw[Pillow ROI Draw]
        ROI_API[GET /api/roi]
    end
    
    subgraph Data["Database (PostgreSQL)"]
        DB[(ROI Records)]
    end
    
    Cam --> Canvas
    Canvas -- jpeg blob --> WS
    WS <--> WS_Server
    WS_Server --> Detect
    Detect --> Draw
    Draw --> WS
    Draw --> ROI_API
    ROI_API --> DB
    
    Ingest --> Detect
```

## Flow
1. Client webcam captures frames
2. Frames sent via WebSocket to backend
3. MediaPipe detects face (no OpenCV)
4. Pillow draws ROI rectangle (no OpenCV)
5. Processed frame returned to client
6. ROI stored in PostgreSQL