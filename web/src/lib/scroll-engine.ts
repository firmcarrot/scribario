/**
 * Custom RAF-based scroll animation engine.
 * Inspired by ForHims' window.R — no GSAP, no AOS, no libraries.
 *
 * Performance: Only runs RAF when actively scrolling. Stops after idle.
 */

export const R = {
  lerp: (start: number, end: number, factor: number) =>
    start + (end - start) * factor,

  clamp: (val: number, min: number, max: number) =>
    Math.min(Math.max(val, min), max),

  remap: (val: number, inMin: number, inMax: number, outMin: number, outMax: number) => {
    const t = R.clamp((val - inMin) / (inMax - inMin), 0, 1);
    return outMin + t * (outMax - outMin);
  },

  iLerp: (val: number, min: number, max: number) =>
    R.clamp((val - min) / (max - min), 0, 1),

  ease: (t: number) => 1 - Math.pow(1 - t, 3),
};

type ScrollCallback = (scrollY: number, windowHeight: number) => void;

class ScrollEngine {
  private callbacks: Map<string, ScrollCallback> = new Map();
  private rafId: number | null = null;
  private running = false;
  private scrollY = 0;
  private targetScrollY = 0;
  private idleFrames = 0;
  private scrollListenerAttached = false;
  private prefersReducedMotion = false;

  start() {
    if (this.running) return;
    this.running = true;
    this.idleFrames = 0;
    this.tick();
  }

  stop() {
    this.running = false;
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  register(id: string, cb: ScrollCallback) {
    this.callbacks.set(id, cb);
    if (!this.scrollListenerAttached) {
      this.scrollListenerAttached = true;
      this.prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.addEventListener("scroll", this.onScroll, { passive: true });
    }
    // Run one initial tick to set positions
    this.targetScrollY = window.scrollY;
    this.scrollY = this.targetScrollY;
    const wh = window.innerHeight;
    cb(this.scrollY, wh);
  }

  unregister(id: string) {
    this.callbacks.delete(id);
    if (this.callbacks.size === 0) {
      this.stop();
      if (this.scrollListenerAttached) {
        window.removeEventListener("scroll", this.onScroll);
        this.scrollListenerAttached = false;
      }
    }
  }

  private onScroll = () => {
    this.targetScrollY = window.scrollY;
    this.idleFrames = 0;
    if (!this.running && this.callbacks.size > 0) {
      this.start();
    }
  };

  private tick = () => {
    if (!this.running) return;

    // Snap immediately for users who prefer reduced motion
    if (this.prefersReducedMotion) {
      this.scrollY = this.targetScrollY;
    } else {
      this.scrollY = R.lerp(this.scrollY, this.targetScrollY, 0.12);
    }

    if (Math.abs(this.scrollY - this.targetScrollY) < 0.5) {
      this.scrollY = this.targetScrollY;
      this.idleFrames++;
    } else {
      this.idleFrames = 0;
    }

    const wh = window.innerHeight;
    this.callbacks.forEach((cb) => cb(this.scrollY, wh));

    // Stop RAF loop after 10 idle frames (~167ms) to save CPU
    if (this.idleFrames > 10) {
      this.stop();
      return;
    }

    this.rafId = requestAnimationFrame(this.tick);
  };
}

let engine: ScrollEngine | null = null;

export function getScrollEngine(): ScrollEngine {
  if (!engine) {
    engine = new ScrollEngine();
  }
  return engine;
}
