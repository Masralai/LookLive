FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python, uv, curl, and OpenGL libraries for OpenCV
RUN apt-get update && apt-get install -y \
    python3.11 python3-pip curl \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml first (layer caching)
COPY pyproject.toml .

# Install dependencies with uv
RUN uv pip install --system --no-cache -r pyproject.toml || true

# Download YOLOv8n model (standard - will auto-download)
RUN python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('Model downloaded')"

# Add non-root user
RUN groupadd -r appgroup -g 1001 && useradd -r -u 1001 -g appgroup -s /bin/sh appuser

# Copy application code
COPY main.py ./
COPY api ./api
COPY services ./services
COPY db ./db
COPY utils ./utils

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]