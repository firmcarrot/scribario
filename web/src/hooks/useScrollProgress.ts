"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { getScrollEngine, R } from "@/lib/scroll-engine";

/**
 * Returns a 0→1 progress value for how far an element has scrolled through the viewport.
 * Attach `ref` to the container element.
 */
export function useScrollProgress(offset = 0) {
  const ref = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0);
  const idRef = useRef(`sp-${Math.random().toString(36).slice(2, 8)}`);

  const update = useCallback(
    (scrollY: number, wh: number) => {
      const el = ref.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const top = rect.top + scrollY;
      const height = rect.height;

      const start = top - wh * (1 - offset);
      const end = top + height - wh * offset;

      const p = R.iLerp(scrollY, start, end);
      setProgress(p);
    },
    [offset]
  );

  useEffect(() => {
    const engine = getScrollEngine();
    const id = idRef.current;
    engine.register(id, update);
    return () => engine.unregister(id);
  }, [update]);

  return { ref, progress };
}
