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
            <a
              href="https://github.com/Masralai/LookLive"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center font-medium transition-all duration-150 bg-transparent border border-ash-border rounded-[999px] px-4 py-2 text-ink-black hover:bg-e6e6e6"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
              GitHub
            </a>
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
            Powered by YOLOv8 for real-time detection without OpenCV.
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
                YOLOv8 delivers real-time detection at 30+ FPS
              </p>
            </div>
            <div className="p-6 bg-canvas-pearl rounded-[7.42183px]">
              <h3 className="text-lg font-medium mb-2">No OpenCV</h3>
              <p className="text-sm text-stone-whisper">
                Lightweight YOLOv8 implementation, no heavy dependencies
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