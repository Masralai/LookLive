# LookLive — Real-Time Face Detection Video Streaming System

A containerized backend API to accept a video feed, process it to detect faces using MTCNN (no OpenCV), store ROI data in PostgreSQL, and return the feed with ROI overlay to a Next.js frontend.

## Quick Start

```bash
docker compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11 + uv |
| Face Detection | MTCNN (no OpenCV) |
| Database | PostgreSQL |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Containerization | Docker Compose |

## Project Structure

```
looklive/
├── backend/               # FastAPI backend
│   ├── api/              # API endpoints
│   ├── services/         # Face detection
│   ├── db/              # Database models
│   ├── utils/           # Utilities
│   ├── main.py          # Application entry
│   ├── pyproject.toml   # uv project config
│   └── Dockerfile
├── frontend/             # Next.js frontend
│   ├── src/
│   │   └── app/         # Next.js app router
│   ├── package.json
│   └── Dockerfile
├── tests/               # Integration tests
├── docs/                # Documentation
│   └── superpowers/
│       └── specs/      # Design specs
├── docker-compose.yml
├── prd.md              # Product requirements
├── DESIGN.md           # Design system
└── sk.md               # Skill plan
```

## PRD Requirements Met

- ✅ 3 API endpoints (POST /api/video/ingest, WebSocket /ws/video, GET /api/roi)
- ✅ No OpenCV (using MTCNN)
- ✅ROI stored in PostgreSQL
- ✅Draw ROI without OpenCV (using Pillow)
- ✅Docker Compose (frontend + backend + PostgreSQL)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://postgres:postgres@db:5432/looklive | PostgreSQL connection |
| `NEXT_PUBLIC_WS_URL` | ws://localhost:8000/ws/video | WebSocket URL |

## License

MIT