# LookLive — Real-Time Face Detection Video Streaming System

A containerized backend API to accept a video feed, process it to detect faces using YOLOv8 (no OpenCV), store ROI data in PostgreSQL, and return the feed with ROI overlay to a Next.js frontend.

## Quick Start

```bash
docker compose up --build
```

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11 |
| Face Detection | YOLOv8 (no OpenCV) |
| Database | PostgreSQL |
| Frontend | Next.js 16 + TypeScript + Tailwind CSS |
| Containerization | Docker Compose |

## Project Structure

```
looklive/
├── backend/               # FastAPI backend
│   ├── api/              # API endpoints (endpoints.py, roi.py)
│   ├── services/         # Face detection (face_detector.py)
│   ├── db/               # Database models (models.py)
│   ├── utils/           # Utilities (draw.py)
│   ├── main.py          # Application entry
│   ├── pyproject.toml   # Python project config
│   ├── yolov8n.pt       # YOLO model weights
│   └── Dockerfile
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js app router
│   │   └── components/ # React components
│   ├── package.json
│   └── Dockerfile
├── scripts/              # Startup scripts
│   └── start-local.sh   # Local development script
├── tests/               # Integration tests
├── docs/                # Documentation
├── docker-compose.yml
├── prd.md               # Product requirements
└── DESIGN.md            # Design system
```

## Features

- **Real-time face detection** via WebSocket connection
- **3 API endpoints** for video ingest, ROI retrieval, and real-time streaming
- **PostgreSQL storage** for ROI data with session and frame tracking
- **No OpenCV** - uses YOLOv8 for detection and Pillow for drawing
- **Docker Compose** for easy deployment
- **Auto-reload** for development

## API Endpoints

### POST /api/video/ingest

Upload a video frame for processing. Returns the processed image with ROI overlay.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**

```json
{
  "status": "ok",
  "roi": {"x": 100, "y": 150, "w": 200, "h": 250, "confidence": 0.95},
  "frame": "<base64 encoded image>"
}
```

### GET /api/roi

Get the latest detected ROI data.

**Response:**

```json
{
  "roi": {"x": 100, "y": 150, "w": 200, "h": 250, "confidence": 0.95}
}
```

### WebSocket /ws/video

Real-time video stream processing. Send binary image data, receive ROI coordinates.

**Client sends:** Binary JPEG image data

**Server sends:**

```json
{
  "roi": {"x": 100, "y": 150, "w": 200, "h": 250, "confidence": 0.95},
  "frame_id": 123
}
```

## Database Schema

**Table: roi_records**

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| session_id | String | Session identifier |
| frame_id | Integer | Frame number within session |
| bbox_x | Integer | Bounding box X coordinate |
| bbox_y | Integer | Bounding box Y coordinate |
| bbox_w | Integer | Bounding box width |
| bbox_h | Integer | Bounding box height |
| confidence | Float | Detection confidence score |
| timestamp | DateTime | Record creation time |

Indexes: `session_id + frame_id`, `session_id`, `timestamp`

## Local Development

For local development without Docker containers:

```bash
./scripts/start-local.sh
```

This script will:

1. Start PostgreSQL container via Docker
2. Open a new terminal for the backend (port 8000)
3. Open a new terminal for the frontend (port 3000)

**Available commands:**

```bash
./scripts/start-local.sh start     # Start all services
./scripts/start-local.sh stop      # Stop all services
./scripts/start-local.sh restart   # Restart all services
./scripts/start-local.sh status   # Show service status
./scripts/start-local.sh db       # Start only PostgreSQL
```

**Requirements:**

- Docker (for PostgreSQL)
- Python 3.11+
- Node.js 18+

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://postgres:postgres@db:5432/looklive | PostgreSQL connection string |
| `NEXT_PUBLIC_WS_URL` | ws://localhost:8000/ws/video | WebSocket URL for frontend |

## PRD Requirements Met

- 3 API endpoints (POST /api/video/ingest, WebSocket /ws/video, GET /api/roi)
- No OpenCV (using YOLOv8)
- ROI stored in PostgreSQL
- Draw ROI without OpenCV (using Pillow)
- Docker Compose (frontend + backend + PostgreSQL)
