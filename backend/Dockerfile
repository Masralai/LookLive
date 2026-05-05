FROM python:3.11-slim

WORKDIR /app

RUN pip install uv && \
    rm -rf /root/.cache/pip

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]