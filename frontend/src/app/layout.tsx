import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LookLive — Real-Time Face Detection",
  description: "Real-time face detection video streaming system with ROI detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-screen bg-canvas-pearl text-ink-black">
        {children}
      </body>
    </html>
  );
}