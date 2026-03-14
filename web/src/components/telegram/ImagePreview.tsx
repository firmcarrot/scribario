"use client";

import { useState } from "react";

interface Props {
  images: { src: string; caption: string }[];
}

export function ImagePreview({ images }: Props) {
  return (
    <div className={`grid gap-1.5 ${images.length > 1 ? "grid-cols-3" : "grid-cols-1"}`}>
      {images.map((img, i) => (
        <ImageCard key={i} src={img.src} caption={img.caption} />
      ))}
    </div>
  );
}

function ImageCard({ src, caption }: { src: string; caption: string }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className="rounded-xl overflow-hidden bg-[#1E1E1E]">
      <div className="relative aspect-[4/5]">
        {!loaded && (
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(90deg, #1E1E1E 25%, #2a2a2a 50%, #1E1E1E 75%)",
              backgroundSize: "200% 100%",
              animation: "shimmer 1.5s infinite",
            }}
          />
        )}
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#1E1E1E]">
            <span className="text-[#737373] text-xs">Image</span>
          </div>
        ) : (
          <img
            src={src}
            alt={caption}
            className={`w-full h-full object-cover transition-all duration-500 ${
              loaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
            }`}
            onLoad={() => setLoaded(true)}
            onError={() => { setError(true); setLoaded(true); }}
          />
        )}
      </div>
      <p className="text-xs text-[#a0a0a0] px-3 py-2 line-clamp-2">{caption}</p>
    </div>
  );
}
