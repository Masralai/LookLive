import { useState, useEffect, useRef } from 'react'

function App() {
  const [connected, setConnected] = useState(false)
  const [status, setStatus] = useState('Disconnected')
  const [roi, setRoi] = useState(null)
  const [error, setError] = useState(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const displayCanvasRef = useRef(null)
  const wsRef = useRef(null)
  const streamRef = useRef(null)

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' }
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      setError('Camera error: ' + err.message)
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/video')
    
    ws.onopen = () => {
      setConnected(true)
      setStatus('Connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.roi) {
          setRoi(data.roi)
        }
        if (data.frame) {
          const displayCanvas = displayCanvasRef.current
          if (displayCanvas) {
            const ctx = displayCanvas.getContext('2d')
            const img = new Image()
            img.onload = () => {
              ctx.drawImage(img, 0, 0)
            }
            img.src = 'data:image/jpeg;base64,' + data.frame
          }
        }
      } catch (e) {
        console.error('Parse error:', e)
      }
    }
    
    ws.onclose = () => {
      setConnected(false)
      setStatus('Disconnected')
    }
    
    ws.onerror = () => {
      setError('WebSocket error')
    }
    
    wsRef.current = ws
  }

  const sendFrame = () => {
    if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
    canvas.toBlob((blob) => {
      if (blob && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(blob)
      }
    }, 'image/jpeg', 0.5)
  }

  useEffect(() => {
    startCamera()
    connectWebSocket()
    
    const interval = setInterval(sendFrame, 100)
    
    return () => {
      clearInterval(interval)
      stopCamera()
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  return (
    <div className="app">
      <h1>LookLive</h1>
      <p className="subtitle">Real-Time Face Detection</p>
      
      <div className="video-container">
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          muted
          style={{ display: 'none' }}
        />
        <canvas ref={canvasRef} width={640} height={480} style={{ display: 'none' }} />
        <canvas ref={displayCanvasRef} className="video-canvas" />
      </div>
      
      <div className="status-bar">
        <span className={`indicator ${connected ? 'connected' : ''}`} />
        <span>{status}</span>
        {roi && (
          <span className="roi-info">
            ROI: {roi.x}, {roi.y} ({roi.w}x{roi.h})
          </span>
        )}
      </div>
      
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default App