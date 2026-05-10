FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv and CPU-only PyTorch first
RUN pip install uv
RUN pip install torch --index-url https://download.pytorch.org/whl/cu124

# Copy pyproject.toml first (layer caching)
COPY pyproject.toml .

# Install dependencies with uv (excluding torch since we installed CPU version)
RUN uv pip install --system --no-cache -r pyproject.toml || true

# Copy YOLOv8n-face model
COPY yolov8n-face.pt .

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