"use client";

import { useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import { PlatformBar } from "@/components/ui/PlatformBar";
import { EmailCapture } from "@/components/ui/EmailCapture";
import Image from "next/image";

const features = [
  { text: "Text what you want", num: "01", desc: "Describe your post in plain language via Telegram" },
  { text: "AI creates 3 options", num: "02", desc: "Get three publish-ready captions and images instantly" },
  { text: "One tap publishes", num: "03", desc: "Approve and post to every platform simultaneously" },
];

export function Hero() {
  const heroRef = useRef<HTMLElement>(null);
  const heroVideoRef = useRef<HTMLVideoElement>(null);
  const heroContentRef = useRef<HTMLDivElement>(null);
  const phoneSectionRef = useRef<HTMLDivElement>(null);
  const phoneVideoRef = useRef<HTMLVideoElement>(null);
  const phoneWrapperRef = useRef<HTMLDivElement>(null);
  const featureRefs = useRef<(HTMLDivElement | null)[]>([]);

  const tryPlayVideo = useCallback(() => {
    const v = heroVideoRef.current;
    if (v && v.paused) v.play().catch(() => {});
    const pv = phoneVideoRef.current;
    if (pv && pv.paused) {
      pv.playbackRate = 1.75;
      pv.play().catch(() => {});
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

    let cachedHeroTop = 0;
    let cachedHeroHeight = 0;
    let cachedPhoneTop = 0;
    const cachePositions = () => {
      const el = heroRef.current;
      const ps = phoneSectionRef.current;
      if (el) {
        cachedHeroTop = el.getBoundingClientRect().top + window.scrollY;
        cachedHeroHeight = el.offsetHeight;
      }
      if (ps) cachedPhoneTop = ps.getBoundingClientRect().top + window.scrollY;
    };
    cachePositions();
    setTimeout(cachePositions, 0);
    window.addEventListener("resize", cachePositions);

    engine.register("hero-scroll", (scrollY, wh) => {
      // Parallax: hero content moves up slightly slower than scroll
      if (heroContentRef.current) {
        const relScroll = scrollY - cachedHeroTop;
        if (relScroll > 0 && relScroll < wh * 1.5) {
          const parallaxY = relScroll * 0.3;
          const fadeOut = 1 - R.ease(R.iLerp(scrollY, cachedHeroTop + wh * 0.2, cachedHeroTop + wh * 0.8));
          heroContentRef.current.style.transform = `translateY(${parallaxY}px)`;
          heroContentRef.current.style.opacity = String(Math.max(0, fadeOut));
        }
      }

      // Phone scroll animations
      const isMobile = window.innerWidth < 750;
      const phoneSection = phoneSectionRef.current;
      if (phoneSection && phoneWrapperRef.current && !isMobile) {
        const pTop = cachedPhoneTop;
        const enterStart = pTop - wh * 0.5;
        const enterEnd = pTop + wh * 0.3;
        const p = R.ease(R.iLerp(scrollY, enterStart, enterEnd));
        const scale = R.lerp(0.85, 1, p);
        const y = R.lerp(60, 0, p);
        const rotateX = R.lerp(15, 0, p);
        phoneWrapperRef.current.style.transform = `perspective(1200px) rotateX(${rotateX}deg) scale(${scale}) translateY(${y}px)`;
        phoneWrapperRef.current.style.opacity = String(p);

        // Features stagger in alongside the phone
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
    <header ref={heroRef} id="hero" className="relative" data-dark>

      {/* ── FULL-BLEED VIDEO HERO ── */}
      <div className="relative overflow-hidden" style={{ minHeight: "100vh" }}>
        {/* Background video — fixed position creates parallax */}
        <video
          ref={heroVideoRef}
          autoPlay
          loop
          muted
          playsInline
          poster="/images/hero-bg-poster.jpg"
          className="absolute inset-0 w-full h-full"
          style={{
            objectFit: "cover",
            objectPosition: "center center",
          }}
          src="/videos/hero-bg.mp4"
        />

        {/* Dark overlay for text legibility */}
        <div
          className="absolute inset-0 z-[1]"
          style={{
            background: "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.7) 100%)",
          }}
        />

        {/* Hero content — scrolls with parallax over fixed video */}
        <div
          ref={heroContentRef}
          className="relative z-10 text-center px-6 flex flex-col items-center justify-center"
          style={{
            minHeight: "100vh",
            paddingTop: "clamp(8rem, 14vw, 14rem)",
            paddingBottom: "clamp(4rem, 8vw, 8rem)",
            willChange: "transform, opacity",
          }}
        >
          <motion.p
            className="font-mono"
            style={{
              fontSize: "0.75rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "rgba(255,255,255,0.5)",
              marginBottom: "clamp(1.5rem, 2.5vw, 2.5rem)",
            }}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            AI Social Media Automation
          </motion.p>

          <motion.h1
            className="font-display font-bold mx-auto"
            style={{
              fontSize: "clamp(3.5rem, 7vw, 7rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.04em",
              color: "#fff",
              maxWidth: "15ch",
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            AI Social Media Automation{" "}
            <span style={{ color: "var(--accent)" }}>in a Text.</span>
          </motion.h1>

          <motion.p
            className="font-body mx-auto"
            style={{
              fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
              lineHeight: 1.5,
              color: "rgba(255,255,255,0.65)",
              maxWidth: "42ch",
              marginTop: "clamp(2rem, 3vw, 3rem)",
              letterSpacing: "-0.01em",
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            Text what you want. Get three publish-ready options — captions, images, video.
            One tap publishes everywhere. 30 seconds, start to finish.
          </motion.p>

          {/* Dual CTAs */}
          <motion.div
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mx-auto"
            style={{ marginTop: "clamp(2.5rem, 4vw, 4rem)" }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.55 }}
          >
            <a
              href="https://t.me/ScribarioBot"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 font-body font-medium transition-all duration-200 hover:scale-[1.02]"
              style={{
                backgroundColor: "var(--accent)",
                color: "#fff",
                borderRadius: 52,
                padding: "16px 32px",
                fontSize: "clamp(0.95rem, 1.1vw, 1.1rem)",
                letterSpacing: "-0.01em",
                minHeight: 48,
                boxShadow: "0 8px 30px rgba(255, 107, 74, 0.35)",
              }}
            >
              <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
              </svg>
              Try it free on Telegram
            </a>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 font-body font-medium transition-all duration-200 hover:opacity-70"
              style={{
                color: "#fff",
                borderRadius: 52,
                padding: "16px 28px",
                fontSize: "clamp(0.95rem, 1.1vw, 1.1rem)",
                letterSpacing: "-0.01em",
                minHeight: 48,
                border: "1px solid rgba(255,255,255,0.2)",
              }}
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              See how it works
              <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 5v14M19 12l-7 7-7-7" />
              </svg>
            </a>
          </motion.div>

          {/* Platform trust bar */}
          <motion.div
            style={{ marginTop: "clamp(3rem, 5vw, 5rem)" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <PlatformBar variant="dark" />
          </motion.div>

          {/* Email capture */}
          <motion.div
            className="flex justify-center"
            style={{ marginTop: "clamp(2rem, 3vw, 3rem)" }}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.85 }}
          >
            <EmailCapture
              headline="Get 5 free posts — no signup required"
              buttonText="Send it"
              source="hero"
              variant="dark"
            />
          </motion.div>
        </div>
      </div>

      {/* ── STICKY PHONE SCROLL ZONE ── */}
      <div
        ref={phoneSectionRef}
        className="relative md:h-[280vh]"
      >
        {/* Desktop: sticky phone — Apple-hero style */}
        <div className="hidden md:block sticky top-[3vh] z-20" style={{ perspective: "1200px" }}>
          <div
            ref={phoneWrapperRef}
            className="flex justify-center"
            style={{
              transform: "perspective(1200px) rotateX(15deg) scale(0.85) translateY(60px)",
              opacity: 0,
              willChange: "transform, opacity",
              transformOrigin: "center top",
            }}
          >
            <div className="relative mx-auto" style={{ width: "min(520px, 40vw)" }}>
              <video
                ref={phoneVideoRef}
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
                alt="Hand holding iPhone showing Scribario AI social media bot creating a post in Telegram"
                width={1792}
                height={2400}
                className="relative z-10 w-full h-auto"
                style={{ filter: "drop-shadow(0 40px 100px rgba(0,0,0,0.3))" }}
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
                    ? { left: "var(--side-padding)" }
                    : { right: "var(--side-padding)", textAlign: "right" as const }),
                  opacity: 0,
                  transform: "translateY(50px) scale(0.95)",
                  willChange: "transform, opacity",
                  maxWidth: "22rem",
                }}
              >
                <span
                  className="font-mono block"
                  style={{
                    fontSize: "0.75rem",
                    letterSpacing: "0.1em",
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
                    fontSize: "clamp(1.75rem, 3vw, 3rem)",
                    letterSpacing: "-0.02em",
                    lineHeight: 1.1,
                    color: "var(--text)",
                  }}
                >
                  {feat.text}
                </span>
                <span
                  className="font-body block mt-3"
                  style={{
                    fontSize: "clamp(0.9rem, 1.2vw, 1.2rem)",
                    lineHeight: 1.5,
                    color: "var(--text-secondary)",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {feat.desc}
                </span>
              </div>
            );
          })}
        </div>

        {/* Mobile: static phone + features */}
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
                alt="Hand holding iPhone showing Scribario AI social media bot"
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
                    letterSpacing: "0.1em",
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
                    letterSpacing: "-0.02em",
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
                    letterSpacing: "-0.01em",
                  }}
                >
                  {feat.desc}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Separator */}
      <div style={{ height: 1, background: "var(--separator)" }} />
    </header>
  );
}
