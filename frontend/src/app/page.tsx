import { VideoStream } from "@/components/VideoStream";
import { Button } from "@/components/ui/Button";

export default function Home() {
  return (
    <main className="min-h-screen bg-canvas-pearl">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-canvas-pearl/80 backdrop-blur-md border-b border-e6e6e6">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold tracking-tight">LookLive</h1>
          <nav className="flex items-center gap-4">
            <Button variant="ghost">About</Button>
            <Button variant="primary">Get Started</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4">
            Real-Time Face Detection
          </h2>
          <p className="text-lg text-stone-whisper max-w-xl mx-auto mb-8">
            Detect faces in real-time video streams with ROI bounding boxes. 
            Powered by MediaPipe for lightning-fast detection without OpenCV.
          </p>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-8">
        <VideoStream />
      </section>

      {/* Features */}
      <section className="py-16 bg-snowdrift-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-canvas-pearl rounded-[7.42183px]">
              <h3 className="text-lg font-medium mb-2">Fast Detection</h3>
              <p className="text-sm text-stone-whisper">
                MediaPipe delivers sub-second face detection at 30+ FPS
              </p>
            </div>
            <div className="p-6 bg-canvas-pearl rounded-[7.42183px]">
              <h3 className="text-lg font-medium mb-2">No OpenCV</h3>
              <p className="text-sm text-stone-whisper">
                Lightweight MediaPipe implementation, no heavy dependencies
              </p>
            </div>
            <div className="p-6 bg-canvas-pearl rounded-[7.42183px]">
              <h3 className="text-lg font-medium mb-2">ROI Storage</h3>
              <p className="text-sm text-stone-whisper">
                All detections stored in PostgreSQL for analytics
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-e6e6e6">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-stone-whisper">
          Built with Next.js + Tailwind CSS + Base44 Design System
        </div>
      </footer>
    </main>
  );
}