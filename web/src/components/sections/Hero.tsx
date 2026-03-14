"use client";

import { useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import Image from "next/image";

const bgTextLines = [
  {
    text: "text it",
    gradient: "linear-gradient(166deg, rgb(255, 107, 74), rgb(229, 85, 58))",
    align: "left" as const,
  },
  {
    text: "approve it",
    gradient: "linear-gradient(166deg, rgb(0, 136, 204), rgb(255, 140, 105))",
    align: "right" as const,
  },
  {
    text: "posted",
    gradient: "linear-gradient(166deg, rgb(255, 107, 74), rgb(0, 136, 204))",
    align: "center" as const,
  },
];

const features = [
  { text: "Text what you want", num: "01", desc: "Describe your post in plain language via Telegram" },
  { text: "AI creates 3 options", num: "02", desc: "Get three publish-ready captions and images instantly" },
  { text: "One tap publishes", num: "03", desc: "Approve and post to every platform simultaneously" },
];

export function Hero() {
  const heroRef = useRef<HTMLElement>(null);
  const phoneSectionRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Direct DOM refs for scroll-driven styles (no setState = no re-renders)
  const gradientBlobRef = useRef<HTMLDivElement>(null);
  const phoneWrapperRef = useRef<HTMLDivElement>(null);
  const featureRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Force video play on any user interaction (handles autoplay policy)
  const tryPlayVideo = useCallback(() => {
    const v = videoRef.current;
    if (v && v.paused) {
      v.playbackRate = 1.75;
      v.play().catch(() => {});
    }
  }, []);

  useEffect(() => {
    tryPlayVideo();
    const handler = () => {
      tryPlayVideo();
      window.removeEventListener("scroll", handler);
      window.removeEventListener("touchstart", handler);
      window.removeEventListener("click", handler);
    };
    window.addEventListener("scroll", handler, { passive: true });
    window.addEventListener("touchstart", handler, { passive: true });
    window.addEventListener("click", handler);
    return () => {
      window.removeEventListener("scroll", handler);
      window.removeEventListener("touchstart", handler);
      window.removeEventListener("click", handler);
    };
  }, [tryPlayVideo]);

  useEffect(() => {
    const engine = getScrollEngine();
    const isMobile = window.innerWidth < 750;

    // Cache element positions — use getBoundingClientRect + scrollY for accuracy
    // (offsetTop can be wrong when contain: layout paint shifts offsetParent)
    let cachedHeroTop = 0;
    let cachedPhoneTop = 0;
    const cachePositions = () => {
      const el = heroRef.current;
      const ps = phoneSectionRef.current;
      if (el) cachedHeroTop = el.getBoundingClientRect().top + window.scrollY;
      if (ps) cachedPhoneTop = ps.getBoundingClientRect().top + window.scrollY;
    };
    cachePositions();
    setTimeout(cachePositions, 0);
    window.addEventListener("resize", cachePositions);

    engine.register("hero-scroll", (scrollY, wh) => {
      const el = heroRef.current;
      if (!el) return;

      const elTop = cachedHeroTop;

      // Gradient blob fades — direct DOM write
      const gradStart = elTop;
      const gradEnd = elTop + wh * 1.2;
      const gradOp = R.lerp(0.8, 0, R.iLerp(scrollY, gradStart, gradEnd));
      if (gradientBlobRef.current) {
        gradientBlobRef.current.style.opacity = String(gradOp);
      }

      // Phone scroll animations — direct DOM write
      const phoneSection = phoneSectionRef.current;
      if (phoneSection && phoneWrapperRef.current && !isMobile) {
        const pTop = cachedPhoneTop;

        const enterStart = pTop - wh * 0.5;
        const enterEnd = pTop + wh * 0.3;
        const p = R.ease(R.iLerp(scrollY, enterStart, enterEnd));
        const scale = R.lerp(0.8, 1, p);
        const y = R.lerp(40, 0, p);
        const rotateX = R.lerp(20, 0, p);

        phoneWrapperRef.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) scale(${scale}) translateY(${y}px)`;
        phoneWrapperRef.current.style.opacity = String(p);

        // Features stagger in — direct DOM write
        const featStart = pTop + wh * 0.6;
        const featSpacing = wh * 0.55;
        features.forEach((_, i) => {
          const ref = featureRefs.current[i];
          if (!ref) return;
          const itemStart = featStart + i * featSpacing;
          const itemEnd = itemStart + wh * 0.35;
          const inP = R.ease(R.iLerp(scrollY, itemStart, itemEnd));
          const fadeOutStart = itemEnd + wh * 0.05;
          const fadeOutEnd = fadeOutStart + wh * 0.25;
          const fadeOut = i < features.length - 1
            ? 1 - R.ease(R.iLerp(scrollY, fadeOutStart, fadeOutEnd))
            : 1;
          const opacity = Math.min(inP, fadeOut);
          const fy = R.lerp(50, 0, inP);
          const fScale = R.lerp(0.95, 1, inP);
          ref.style.opacity = String(opacity);
          ref.style.transform = `translateY(${fy}px) scale(${fScale})`;
        });
      }
    });

    return () => {
      engine.unregister("hero-scroll");
      window.removeEventListener("resize", cachePositions);
    };
  }, []);

  return (
    <header ref={heroRef} id="hero" className="relative" style={{ paddingTop: 100, contain: "layout paint" }}>

      {/* ── Ambient gradient blob — NO blur(), radial gradients are already soft ── */}
      <div
        ref={gradientBlobRef}
        className="absolute inset-0 z-0 pointer-events-none"
        style={{ opacity: 0.8 }}
      >
        <div
          className="absolute"
          style={{
            top: "-10%",
            left: "-10%",
            width: "120%",
            height: "70%",
            backgroundImage: `
              radial-gradient(ellipse 70% 50% at 65% 40%, rgba(255, 107, 74, 0.2) 0px, transparent 100%),
              radial-gradient(ellipse 60% 50% at 35% 60%, rgba(0, 136, 204, 0.12) 0px, transparent 100%),
              radial-gradient(ellipse 50% 40% at 50% 30%, rgba(255, 140, 105, 0.15) 0px, transparent 100%)
            `,
          }}
        />
      </div>

      {/* ── H1 — no container, no card, text sits directly on the page ── */}
      <div className="relative z-10 text-center" style={{ paddingBottom: "2vw" }}>
        <motion.p
          className="font-mono"
          style={{
            fontSize: "clamp(0.65rem, 0.9vw, 0.9rem)",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            color: "var(--text-secondary)",
            marginBottom: "clamp(1rem, 2vw, 2rem)",
          }}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          AI-powered social media
        </motion.p>

        <motion.h1
          className="relative z-10 text-center font-display font-bold px-6 md:px-0"
          style={{
            fontSize: "clamp(2.5rem, 5.625vw, 5.625rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.055em",
            color: "var(--text)",
          }}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          Your social media team in{" "}
          <span style={{ color: "var(--accent)" }}>
            a text.
          </span>
        </motion.h1>

        <motion.p
          className="font-body px-6"
          style={{
            fontSize: "clamp(1rem, 1.4vw, 1.4rem)",
            lineHeight: 1.6,
            color: "var(--text-secondary)",
            maxWidth: "38ch",
            textAlign: "center",
            marginTop: "clamp(3rem, 5vw, 5rem)",
            marginLeft: "auto",
            marginRight: "auto",
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          Text a message. Get three publish-ready options.
          Post everywhere — in 30 seconds.
        </motion.p>
      </div>

      {/* ── STICKY PHONE SCROLL ZONE ── */}
      <div
        ref={phoneSectionRef}
        className="relative md:h-[280vh]"
      >
        {/* Desktop: sticky phone */}
        <div className="hidden md:block sticky top-[5vh] z-20" style={{ perspective: "1000px" }}>
          <div
            ref={phoneWrapperRef}
            className="flex justify-center"
            style={{
              transform: "perspective(1000px) rotateX(20deg) scale(0.8) translateY(40px)",
              opacity: 0,
              willChange: "transform, opacity",
              transformOrigin: "center top",
            }}
          >
            <div className="relative mx-auto" style={{ width: "min(480px, 36vw)" }}>
              <video
                ref={videoRef}
                autoPlay
                loop
                muted
                playsInline
                poster="/images/phone-demo-poster.jpg"
                className="absolute z-0"
                style={{
                  top: "22.2%",
                  left: "30.7%",
                  width: "38.1%",
                  height: "59.5%",
                  objectFit: "cover",
                  borderRadius: "3.5%",
                }}
                src="/videos/phone-demo-web.mp4"
              />
              <Image
                src="/images/hand-phone.webp"
                alt="Hand holding iPhone showing Scribario bot"
                width={1792}
                height={2400}
                className="relative z-10 w-full h-auto"
                style={{ filter: "drop-shadow(0 25px 50px rgba(0,0,0,0.25))" }}
                priority
              />
            </div>
          </div>
        </div>

        {/* Desktop: feature overlays */}
        <div className="hidden md:block absolute inset-0 z-30 pointer-events-none">
          {features.map((feat, i) => {
            const topPct = 38 + i * 18;
            const isLeft = i % 2 === 0;
            return (
              <div
                key={feat.text}
                ref={(el) => { featureRefs.current[i] = el; }}
                className="absolute"
                style={{
                  top: `${topPct}%`,
                  ...(isLeft
                    ? { left: "clamp(2rem, 8vw, 8rem)" }
                    : { right: "clamp(2rem, 8vw, 8rem)", textAlign: "right" as const }),
                  opacity: 0,
                  transform: "translateY(50px) scale(0.95)",
                  willChange: "transform, opacity",
                  maxWidth: "22rem",
                }}
              >
                <span
                  className="font-mono block"
                  style={{
                    fontSize: "clamp(0.6rem, 0.75vw, 0.8rem)",
                    letterSpacing: "0.2em",
                    color: "var(--accent)",
                    marginBottom: "0.75rem",
                    textTransform: "uppercase",
                  }}
                >
                  Step {feat.num}
                </span>
                <span
                  className="font-display font-bold block"
                  style={{
                    fontSize: "clamp(1.5rem, 3vw, 3rem)",
                    letterSpacing: "-0.0475em",
                    lineHeight: 1.1,
                    color: "var(--text)",
                  }}
                >
                  {feat.text}
                </span>
                <span
                  className="font-body block mt-3"
                  style={{
                    fontSize: "clamp(0.85rem, 1.1vw, 1.1rem)",
                    lineHeight: 1.5,
                    color: "var(--text-secondary)",
                  }}
                >
                  {feat.desc}
                </span>
              </div>
            );
          })}
        </div>

        {/* Mobile: static phone + features (no scroll animation, no extra video) */}
        <div className="md:hidden pt-8">
          <div className="flex justify-center px-6">
            <div className="relative mx-auto" style={{ width: "min(320px, 78vw)" }}>
              <video
                autoPlay
                loop
                muted
                playsInline
                preload="none"
                poster="/images/phone-demo-poster.jpg"
                className="absolute z-0"
                style={{
                  top: "22.2%",
                  left: "30.7%",
                  width: "38.1%",
                  height: "59.5%",
                  objectFit: "cover",
                  borderRadius: "3.5%",
                }}
                onPlay={(e) => { (e.target as HTMLVideoElement).playbackRate = 1.75; }}
                src="/videos/phone-demo-web.mp4"
              />
              <Image
                src="/images/hand-phone.webp"
                alt="Hand holding iPhone showing Scribario bot"
                width={1792}
                height={2400}
                className="relative z-10 w-full h-auto"
                style={{ filter: "drop-shadow(0 25px 50px rgba(0,0,0,0.25))" }}
              />
            </div>
          </div>
          <div className="flex flex-col gap-10 pt-12 pb-8 px-8">
            {features.map((feat) => (
              <motion.div
                key={feat.text}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                <span
                  className="font-mono block"
                  style={{
                    fontSize: "0.65rem",
                    letterSpacing: "0.2em",
                    color: "var(--accent)",
                    marginBottom: "0.5rem",
                    textTransform: "uppercase",
                  }}
                >
                  Step {feat.num}
                </span>
                <span
                  className="font-display font-bold block"
                  style={{
                    fontSize: "clamp(1.25rem, 3.5vw, 1.5rem)",
                    letterSpacing: "-0.0475em",
                    lineHeight: 1.1,
                    color: "var(--text)",
                  }}
                >
                  {feat.text}
                </span>
                <span
                  className="font-body block mt-2"
                  style={{
                    fontSize: "0.9rem",
                    lineHeight: 1.5,
                    color: "var(--text-secondary)",
                  }}
                >
                  {feat.desc}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Massive background text (decorative) */}
      <div
        aria-hidden="true"
        className="overflow-hidden"
        style={{ paddingTop: "15vh", paddingBottom: "10vh" }}
      >
        {bgTextLines.map((line, i) => (
          <div
            key={line.text}
            className="font-display font-bold select-none"
            style={{
              fontSize: "clamp(5rem, 19.4vw, 19.4rem)",
              lineHeight: 1,
              letterSpacing: "-0.0575em",
              textAlign: line.align,
              backgroundImage: line.gradient,
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              paddingTop: i > 0 ? "10vh" : 0,
              marginLeft: line.align === "left" ? "-1.39vw" : 0,
            }}
          >
            {line.text}
          </div>
        ))}
      </div>

      {/* Hero body copy — gradient text */}
      <div
        className="px-[clamp(2rem,10.83vw,10.83rem)]"
        style={{ paddingBottom: "clamp(6rem, 17.36vw, 17.36rem)" }}
      >
        <p
          className="font-body"
          style={{
            fontSize: "clamp(2rem, 5.9vw, 5.9rem)",
            lineHeight: 1.15,
            letterSpacing: "-0.0475em",
            backgroundImage: "linear-gradient(166deg, rgb(255, 107, 74) 1%, rgb(0, 136, 204) 39%, rgb(0, 0, 0) 75%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Best-in-class social media automation. Text a message, get three options, publish everywhere — in 30 seconds.
        </p>
      </div>

      {/* Separator */}
      <div style={{ height: 1, background: "var(--separator)" }} />
    </header>
  );
}
