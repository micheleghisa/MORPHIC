"use client";

import { useRef, useState, useCallback } from "react";

export default function BeforeAfterSlider({
  beforeImage,   // base64 or URL
  afterImage,    // base64 or URL
  beforeLabel = "Current",
  afterLabel = "After Glow-Up",
}: {
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState(50);
  const dragging = useRef(false);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      setPosition((x / rect.width) * 100);
    },
    []
  );

  return (
    <div
      ref={containerRef}
      className="relative w-full aspect-[4/3] rounded-2xl overflow-hidden cursor-ew-resize select-none bg-[#1a1b1c]"
      onMouseDown={() => { dragging.current = true; }}
      onMouseUp={() => { dragging.current = false; }}
      onMouseLeave={() => { dragging.current = false; }}
      onMouseMove={(e) => { if (dragging.current) handleMove(e.clientX); }}
      onTouchMove={(e) => { handleMove(e.touches[0].clientX); }}
    >
      {/* After image (full background) */}
      <img
        src={afterImage.startsWith("data:") ? afterImage : `data:image/png;base64,${afterImage}`}
        alt={afterLabel}
        className="absolute inset-0 w-full h-full object-contain bg-[#f8f9f9]"
        draggable={false}
      />

      {/* Before image (revealed by slider, clipped from left) */}
      <div
        className="absolute inset-0"
        style={{ clipPath: `inset(0 0 0 ${100 - position}%)` }}
      >
        <img
          src={beforeImage.startsWith("data:") ? beforeImage : `data:image/png;base64,${beforeImage}`}
          alt={beforeLabel}
          className="absolute inset-0 w-full h-full object-contain bg-[#f5f3f0]"
          draggable={false}
        />
      </div>

      {/* Slider line */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_0_1px_rgba(0,0,0,0.05)] pointer-events-none"
        style={{ left: `${position}%` }}
      />

      {/* Handle */}
      <div
        className="absolute top-1/2 -translate-y-1/2 w-11 h-11 bg-white rounded-full shadow-[0_2px_12px_rgba(0,0,0,0.15)] flex items-center justify-center cursor-ew-resize z-10 hover:shadow-[0_4px_20px_rgba(0,0,0,0.2)] transition-shadow"
        style={{ left: `${position}%`, transform: `translate(-50%, -50%)` }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1a1b1c" strokeWidth="1.5">
          <path d="M8 4l-6 8 6 8M16 4l6 8-6 8" />
        </svg>
      </div>

      {/* Labels */}
      <span className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm text-[11px] font-medium px-3 py-1.5 rounded-full text-[#1a1b1c] shadow-sm">
        {afterLabel}
      </span>
      <span className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm text-[11px] font-medium px-3 py-1.5 rounded-full text-[#5f6468] shadow-sm">
        {beforeLabel}
      </span>
    </div>
  );
}
