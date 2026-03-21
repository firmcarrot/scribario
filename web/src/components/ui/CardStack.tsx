"use client";

import * as React from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

function cn(...classes: Array<string | undefined | null | false>) {
  return classes.filter(Boolean).join(" ");
}

export type CardStackItem = {
  id: string | number;
  title: string;
  description?: string;
  imageSrc?: string;
  tag?: string;
};

export type CardStackProps<T extends CardStackItem> = {
  items: T[];
  initialIndex?: number;
  maxVisible?: number;
  cardWidth?: number;
  cardHeight?: number;
  overlap?: number;
  spreadDeg?: number;
  perspectivePx?: number;
  depthPx?: number;
  tiltXDeg?: number;
  activeLiftPx?: number;
  activeScale?: number;
  inactiveScale?: number;
  springStiffness?: number;
  springDamping?: number;
  loop?: boolean;
  autoAdvance?: boolean;
  intervalMs?: number;
  pauseOnHover?: boolean;
  showDots?: boolean;
  className?: string;
  onChangeIndex?: (index: number, item: T) => void;
  renderCard?: (item: T, state: { active: boolean }) => React.ReactNode;
};

function wrapIndex(n: number, len: number) {
  if (len <= 0) return 0;
  return ((n % len) + len) % len;
}

function signedOffset(i: number, active: number, len: number, loop: boolean) {
  const raw = i - active;
  if (!loop || len <= 1) return raw;
  const alt = raw > 0 ? raw - len : raw + len;
  return Math.abs(alt) < Math.abs(raw) ? alt : raw;
}

export function CardStack<T extends CardStackItem>({
  items,
  initialIndex = 0,
  maxVisible = 7,
  cardWidth: cardWidthProp = 520,
  cardHeight: cardHeightProp = 320,
  overlap = 0.48,
  spreadDeg = 48,
  perspectivePx = 1100,
  depthPx = 140,
  tiltXDeg = 12,
  activeLiftPx = 22,
  activeScale = 1.03,
  inactiveScale = 0.94,
  springStiffness = 280,
  springDamping = 28,
  loop = true,
  autoAdvance = false,
  intervalMs = 2800,
  pauseOnHover = true,
  showDots = true,
  className,
  onChangeIndex,
  renderCard,
}: CardStackProps<T>) {
  const reduceMotion = useReducedMotion();
  const len = items.length;

  // Responsive card sizing — shrink on mobile to prevent overflow
  const [viewportWidth, setViewportWidth] = React.useState(0);
  React.useEffect(() => {
    const update = () => setViewportWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);
  const cardWidth = viewportWidth > 0 ? Math.min(cardWidthProp, viewportWidth - 48) : cardWidthProp;
  const cardHeight = Math.round(cardHeightProp * (cardWidth / cardWidthProp));

  // Responsive: fewer side cards + less overlap on mobile
  const effectiveMaxVisible = viewportWidth > 0 && viewportWidth < 640 ? Math.min(maxVisible, 3) : viewportWidth < 768 ? Math.min(maxVisible, 5) : maxVisible;
  const effectiveOverlap = viewportWidth > 0 && viewportWidth < 640 ? Math.min(overlap, 0.35) : overlap;
  const effectiveSpreadDeg = viewportWidth > 0 && viewportWidth < 640 ? Math.min(spreadDeg, 20) : spreadDeg;

  const [active, setActive] = React.useState(() => wrapIndex(initialIndex, len));
  const [hovering, setHovering] = React.useState(false);

  React.useEffect(() => {
    setActive((a) => wrapIndex(a, len));
  }, [len]);

  React.useEffect(() => {
    if (!len) return;
    onChangeIndex?.(active, items[active]!);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  const maxOffset = Math.max(0, Math.floor(effectiveMaxVisible / 2));
  const cardSpacing = Math.max(10, Math.round(cardWidth * (1 - effectiveOverlap)));
  const stepDeg = maxOffset > 0 ? effectiveSpreadDeg / maxOffset : 0;

  const canGoPrev = loop || active > 0;
  const canGoNext = loop || active < len - 1;

  const prev = React.useCallback(() => {
    if (!len || !canGoPrev) return;
    setActive((a) => wrapIndex(a - 1, len));
  }, [canGoPrev, len]);

  const next = React.useCallback(() => {
    if (!len || !canGoNext) return;
    setActive((a) => wrapIndex(a + 1, len));
  }, [canGoNext, len]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft") prev();
    if (e.key === "ArrowRight") next();
  };

  React.useEffect(() => {
    if (!autoAdvance || reduceMotion || !len) return;
    if (pauseOnHover && hovering) return;

    const id = window.setInterval(() => {
      if (loop || active < len - 1) next();
    }, Math.max(700, intervalMs));

    return () => window.clearInterval(id);
  }, [autoAdvance, intervalMs, hovering, pauseOnHover, reduceMotion, len, loop, active, next]);

  if (!len) return null;

  return (
    <div
      className={cn("w-full", className)}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <div
        className="relative w-full"
        style={{ height: Math.max(380, cardHeight + 80) }}
        tabIndex={0}
        onKeyDown={onKeyDown}
        role="region"
        aria-label="Business type showcase"
      >
        {/* Subtle glow behind cards */}
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 mx-auto h-40 w-[76%] rounded-full blur-3xl"
          style={{ background: "rgba(255, 107, 74, 0.08)" }}
          aria-hidden="true"
        />

        <div
          className="absolute inset-0 flex items-end justify-center"
          style={{ perspective: `${perspectivePx}px` }}
        >
          <AnimatePresence initial={false}>
            {items.map((item, i) => {
              const off = signedOffset(i, active, len, loop);
              const abs = Math.abs(off);
              const visible = abs <= maxOffset;
              if (!visible) return null;

              const rotateZ = off * stepDeg;
              const x = off * cardSpacing;
              const y = abs * 10;
              const z = -abs * depthPx;
              const isActive = off === 0;
              const scale = isActive ? activeScale : inactiveScale;
              const lift = isActive ? -activeLiftPx : 0;
              const rotateX = isActive ? 0 : tiltXDeg;
              const zIndex = 100 - abs;

              const dragProps = isActive
                ? {
                    drag: "x" as const,
                    dragConstraints: { left: 0, right: 0 },
                    dragElastic: 0.18,
                    onDragEnd: (
                      _e: unknown,
                      info: { offset: { x: number }; velocity: { x: number } },
                    ) => {
                      if (reduceMotion) return;
                      const travel = info.offset.x;
                      const v = info.velocity.x;
                      const threshold = Math.min(160, cardWidth * 0.22);
                      if (travel > threshold || v > 650) prev();
                      else if (travel < -threshold || v < -650) next();
                    },
                  }
                : {};

              return (
                <motion.div
                  key={item.id}
                  className={cn(
                    "absolute bottom-0 rounded-2xl overflow-hidden shadow-xl",
                    "will-change-transform select-none",
                    isActive ? "cursor-grab active:cursor-grabbing" : "cursor-pointer",
                  )}
                  style={{
                    width: cardWidth,
                    height: cardHeight,
                    zIndex,
                    transformStyle: "preserve-3d",
                    border: "1px solid rgba(255,255,255,0.1)",
                  }}
                  initial={
                    reduceMotion
                      ? false
                      : { opacity: 0, y: y + 40, x, rotateZ, rotateX, scale }
                  }
                  animate={{
                    opacity: 1,
                    x,
                    y: y + lift,
                    rotateZ,
                    rotateX,
                    scale,
                  }}
                  transition={{
                    type: "spring",
                    stiffness: springStiffness,
                    damping: springDamping,
                  }}
                  onClick={() => setActive(i)}
                  {...dragProps}
                >
                  <div
                    className="h-full w-full"
                    style={{
                      transform: `translateZ(${z}px)`,
                      transformStyle: "preserve-3d",
                    }}
                  >
                    {renderCard ? (
                      renderCard(item, { active: isActive })
                    ) : (
                      <DefaultCard item={item} active={isActive} />
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>

      {/* Dots */}
      {showDots && (
        <div className="mt-6 flex items-center justify-center gap-0">
          {items.map((it, idx) => (
            <button
              key={it.id}
              onClick={() => setActive(idx)}
              className="flex items-center justify-center"
              style={{ width: 32, height: 44 }}
              aria-label={`Go to ${it.title}`}
            >
              <span
                className="block rounded-full transition-colors duration-200"
                style={{
                  width: 8,
                  height: 8,
                  backgroundColor: idx === active ? "var(--accent)" : "rgba(255,255,255,0.3)",
                }}
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function DefaultCard({ item, active }: { item: CardStackItem; active: boolean }) {
  return (
    <div className="relative h-full w-full">
      {item.imageSrc ? (
        <img
          src={item.imageSrc}
          alt={item.title}
          className="h-full w-full object-cover"
          draggable={false}
          loading="lazy"
        />
      ) : (
        <div
          className="flex h-full w-full items-center justify-center"
          style={{ background: "rgba(255,255,255,0.05)" }}
        >
          <span style={{ color: "rgba(255,255,255,0.3)" }}>No image</span>
        </div>
      )}

      {/* Gradient overlay for text readability */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

      {/* Content */}
      <div className="relative z-10 flex h-full flex-col justify-end p-5">
        {item.tag && (
          <span
            className="font-mono mb-2 text-xs uppercase tracking-widest"
            style={{ color: "var(--accent)" }}
          >
            {item.tag}
          </span>
        )}
        <div
          className="truncate font-display font-bold text-lg"
          style={{ color: "#fff", letterSpacing: "-0.0475em" }}
        >
          {item.title}
        </div>
        {item.description && (
          <div
            className="mt-1 line-clamp-2 text-sm"
            style={{ color: "rgba(255,255,255,0.7)" }}
          >
            {item.description}
          </div>
        )}
        {active && (
          <motion.div
            className="mt-3 h-0.5 rounded-full"
            style={{ backgroundColor: "var(--accent)" }}
            initial={{ width: 0 }}
            animate={{ width: 48 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          />
        )}
      </div>
    </div>
  );
}
