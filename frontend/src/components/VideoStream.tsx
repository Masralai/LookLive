"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface ROIData {
  x: number;
  y: number;
  w: number;
  h: number;
  confidence?: number;
}

interface VideoStreamProps {
  onROIChange?: (roi: ROIData | null) => void;
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/video";

const SMOOTH_FACTOR = 0.15;
const CONFIDENCE_THRESHOLD = 0.5;
const BOX_PADDING = 0.20;

export function VideoStream({ onROIChange }: VideoStreamProps) {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<"disconnected" | "connecting" | "connected" | "error">("disconnected");
  const [roi, setRoi] = useState<ROIData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 640, height: 480 });

  const smoothedRoiRef = useRef<ROIData | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationRef = useRef<number>(0);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      return true;
    } catch (err) {
      setError(`Camera error: ${err instanceof Error ? err.message : "Unknown error"}`);
      return false;
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      setStatus("connected");
      smoothedRoiRef.current = null;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.roi) {
          const newROI = data.roi;

          if (newROI.confidence && newROI.confidence >= CONFIDENCE_THRESHOLD) {
            if (!smoothedRoiRef.current) {
              smoothedRoiRef.current = { ...newROI };
            } else {
              smoothedRoiRef.current = {
                x: Math.round(smoothedRoiRef.current.x + SMOOTH_FACTOR * (newROI.x - smoothedRoiRef.current.x)),
                y: Math.round(smoothedRoiRef.current.y + SMOOTH_FACTOR * (newROI.y - smoothedRoiRef.current.y)),
                w: Math.round(smoothedRoiRef.current.w + SMOOTH_FACTOR * (newROI.w - smoothedRoiRef.current.w)),
                h: Math.round(smoothedRoiRef.current.h + SMOOTH_FACTOR * (newROI.h - smoothedRoiRef.current.h)),
                confidence: newROI.confidence
              };
            }
            setRoi(smoothedRoiRef.current);
            onROIChange?.(smoothedRoiRef.current);
          }
        }
      } catch (e) {
        console.error("Parse error:", e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setStatus("disconnected");
    };

    ws.onerror = () => {
      setStatus("error");
      setError("WebSocket connection failed");
    };

    wsRef.current = ws;
  }, [onROIChange]);

  const sendFrame = useCallback(() => {
    if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx || !videoRef.current) return;

    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(blob);
      }
    }, "image/jpeg", 0.5);
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (connected) {
      interval = setInterval(sendFrame, 30); // ~33 FPS for smoother tracking
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [connected, sendFrame]);

  useEffect(() => {
    startCamera();
    connectWebSocket();

    const canvas = canvasRef.current;
    if (canvas) {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          setCanvasSize({
            width: entry.contentRect.width,
            height: entry.contentRect.height
          });
        }
      });
      resizeObserver.observe(canvas);
      return () => resizeObserver.disconnect();
    }
  }, [startCamera, connectWebSocket, stopCamera]);

  return (
    <div className="relative w-full max-w-3xl mx-auto">
      <div className="relative bg-ink-black rounded-[7.42183px] overflow-hidden aspect-video">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="hidden w-full h-full object-cover"
        />
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="w-full h-full object-cover"
        />
        
        {/* ROI Overlay */}
        {roi && (() => {
          const scaleX = canvasSize.width / 640;
          const scaleY = canvasSize.height / 480;
          
          const expandedW = roi.w * (1 + BOX_PADDING);
          const expandedH = roi.h * (1 + BOX_PADDING);
          const offsetX = (expandedW - roi.w) / 2;
          const offsetY = (expandedH - roi.h) / 2;
          
          return (
            <div
              className="absolute border-2 border-lime-spritz pointer-events-none"
              style={{
                left: `${(roi.x - offsetX) * scaleX}px`,
                top: `${(roi.y - offsetY) * scaleY}px`,
                width: `${expandedW * scaleX}px`,
                height: `${expandedH * scaleY}px`,
              }}
            />
          );
        })()}
      </div>

      {/* Status Bar */}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                status === "connected"
                  ? "bg-lime-spritz"
                  : status === "connecting"
                  ? "bg-sunset-orange animate-pulse"
                  : "bg-ash-border"
              }`}
            />
            <span className="text-sm text-stone-whisper capitalize">{status}</span>
          </div>
          
          {roi && (
            <span className="text-sm font-mono text-stone-whisper">
              ROI: ({roi.x}, {roi.y}) {roi.w}×{roi.h}
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 text-sm text-sunset-orange">{error}</div>
      )}
    </div>
  );
}