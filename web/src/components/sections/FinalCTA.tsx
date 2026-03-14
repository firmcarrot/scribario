"use client";

import { useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import Image from "next/image";

const scrollTexts = [
  { text: "Open Telegram", align: "left" as const },
  { text: "Text your idea", align: "right" as const },
  { text: "Done.", align: "left" as const },
];

export function FinalCTA() {
  const sectionRef = useRef<HTMLElement>(null);
  const phoneSectionRef = useRef<HTMLDivElement>(null);
  const phoneWrapperRef = useRef<HTMLDivElement>(null);
  const textRefs = useRef<(HTMLDivElement | null)[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const tryPlayVideo = useCallback(() => {
    const v = videoRef.current;
    if (v && v.paused) {
      v.playbackRate = 1.75;
      v.play().catch(() => {});
    }
  }, []);

  const pauseVideo = useCallback(() => {
    const v = videoRef.current;
    if (v && !v.paused) v.pause();
  }, []);

  // IntersectionObserver for video — only one video playing at a time
  useEffect(() => {
    if (window.innerWidth < 750 || !videoRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            tryPlayVideo();
            const heroVideo = document.querySelector("#hero video") as HTMLVideoElement | null;
            if (heroVideo && !heroVideo.paused) heroVideo.pause();
          } else {
            pauseVideo();
            const heroVideo = document.querySelector("#hero video") as HTMLVideoElement | null;
            if (heroVideo) {
              const heroRect = heroVideo.getBoundingClientRect();
              if (heroRect.top < window.innerHeight && heroRect.bottom > 0) {
                heroVideo.play().catch(() => {});
              }
            }
          }
        });
      },
      { threshold: 0.1 }
    );
    observerRef.current.observe(videoRef.current);

    return () => { observerRef.current?.disconnect(); };
  }, [tryPlayVideo, pauseVideo]);

  // Scroll engine for desktop phone + text overlays
  useEffect(() => {
    const engine = getScrollEngine();
    const isMobile = window.innerWidth < 750;

    let cachedPhoneTop = 0;
    const cachePositions = () => {
      const ps = phoneSectionRef.current;
      if (ps) cachedPhoneTop = ps.getBoundingClientRect().top + window.scrollY;
    };
    cachePositions();
    setTimeout(cachePositions, 0);
    window.addEventListener("resize", cachePositions);

    engine.register("final-cta-scroll", (scrollY, wh) => {
      if (isMobile) return;

      const pw = phoneWrapperRef.current;
      if (pw) {
        const pTop = cachedPhoneTop;
        const enterStart = pTop - wh * 0.5;
        const enterEnd = pTop + wh * 0.3;
        const p = R.ease(R.iLerp(scrollY, enterStart, enterEnd));
        const scale = R.lerp(0.85, 1, p);
        const rotateX = R.lerp(15, 0, p);
        pw.style.transform = `perspective(1000px) rotateX(${rotateX}deg) scale(${scale})`;
        pw.style.opacity = String(p);
      }

      const textStart = cachedPhoneTop + wh * 0.4;
      const textSpacing = wh * 0.45;
      scrollTexts.forEach((_, i) => {
        const ref = textRefs.current[i];
        if (!ref) return;
        const itemStart = textStart + i * textSpacing;
        const itemEnd = itemStart + wh * 0.3;
        const inP = R.ease(R.iLerp(scrollY, itemStart, itemEnd));
        const fadeOutStart = itemEnd + wh * 0.05;
        const fadeOutEnd = fadeOutStart + wh * 0.2;
        const fadeOut = i < scrollTexts.length - 1
          ? 1 - R.ease(R.iLerp(scrollY, fadeOutStart, fadeOutEnd))
          : 1;
        const opacity = Math.min(inP, fadeOut);
        const fy = R.lerp(40, 0, inP);
        ref.style.opacity = String(opacity);
        ref.style.transform = `translateY(${fy}px)`;
      });
    });

    return () => {
      engine.unregister("final-cta-scroll");
      window.removeEventListener("resize", cachePositions);
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      id="final-cta"
      data-dark
      aria-labelledby="final-cta-heading"
      style={{
        backgroundColor: "var(--bg-dark)",
        contain: "layout paint",
      }}
    >
      {/* DESKTOP: Sticky phone scroll zone FIRST */}
      <div
        ref={phoneSectionRef}
        className="relative hidden md:block"
        style={{ height: "200vh" }}
      >
        <div className="sticky top-[5vh] z-20" style={{ perspective: "1000px" }}>
          <div
            ref={phoneWrapperRef}
            className="flex justify-center"
            style={{
              transform: "perspective(1000px) rotateX(15deg) scale(0.85)",
              opacity: 0,
              willChange: "transform, opacity",
              transformOrigin: "center top",
            }}
          >
            <div className="relative mx-auto" style={{ width: "min(440px, 32vw)" }}>
              <video
                ref={videoRef}
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
                src="/videos/phone-demo-web.mp4"
              />
              <Image
                src="/images/hand-phone.webp"
                alt="Hand holding iPhone showing Scribario bot"
                width={1792}
                height={2400}
                className="relative z-10 w-full h-auto"
                style={{ filter: "drop-shadow(0 25px 50px rgba(0,0,0,0.5))" }}
              />
            </div>
          </div>
        </div>

        {/* Scroll text overlays */}
        <div className="absolute inset-0 z-30 pointer-events-none">
          {scrollTexts.map((item, i) => {
            const topPct = 35 + i * 20;
            const isLeft = item.align === "left";
            return (
              <div
                key={item.text}
                ref={(el) => { textRefs.current[i] = el; }}
                className="absolute"
                style={{
                  top: `${topPct}%`,
                  ...(isLeft
                    ? { left: "clamp(2rem, 8vw, 8rem)" }
                    : { right: "clamp(2rem, 8vw, 8rem)", textAlign: "right" as const }),
                  opacity: 0,
                  transform: "translateY(40px)",
                  willChange: "transform, opacity",
                }}
              >
                <span
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(1.5rem, 3vw, 3rem)",
                    letterSpacing: "-0.0475em",
                    lineHeight: 1.1,
                    color: "#fff",
                  }}
                >
                  {item.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* MOBILE: Static phone with poster only */}
      <div className="md:hidden pt-8 pb-8">
        <div className="flex justify-center px-6">
          <div className="relative mx-auto" style={{ width: "min(280px, 65vw)" }}>
            <Image
              src="/images/phone-demo-poster.jpg"
              alt="Scribario bot conversation"
              width={360}
              height={780}
              className="absolute z-0"
              style={{
                top: "22.2%",
                left: "30.7%",
                width: "38.1%",
                height: "59.5%",
                objectFit: "cover",
                borderRadius: "3.5%",
              }}
            />
            <Image
              src="/images/hand-phone.webp"
              alt="Hand holding iPhone showing Scribario bot"
              width={1792}
              height={2400}
              className="relative z-10 w-full h-auto"
              style={{ filter: "drop-shadow(0 25px 50px rgba(0,0,0,0.5))" }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-6 pt-10 px-8">
          {scrollTexts.map((item, i) => (
            <motion.p
              key={item.text}
              className="font-display font-bold"
              style={{
                fontSize: "1.5rem",
                letterSpacing: "-0.0475em",
                color: "#fff",
                textAlign: item.align === "right" ? "right" : "left",
              }}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              {item.text}
            </motion.p>
          ))}
        </div>
      </div>

      {/* Massive heading — NOW AT THE BOTTOM after phone scroll */}
      <div className="px-6 md:px-16" style={{ paddingTop: "clamp(4rem, 11.11vw, 11.11rem)" }}>
        <motion.h2
          id="final-cta-heading"
          className="font-display font-bold"
          aria-label="Stop scrolling. Start posting."
          style={{
            fontSize: "clamp(3rem, 15vw, 15rem)",
            lineHeight: 1,
            letterSpacing: "-0.0575em",
            backgroundImage: "linear-gradient(93deg, rgb(255, 107, 74) -1%, rgba(0, 136, 204, 0.8) 34%, rgba(255,255,255,0.7) 85%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <span className="block">Stop</span>
          <span className="block text-right">scrolling.</span>
        </motion.h2>
      </div>

      {/* Body copy */}
      <div
        className="px-[clamp(2rem,10.83vw,10.83rem)]"
        style={{
          paddingTop: "clamp(4rem, 8vw, 8rem)",
          paddingBottom: "clamp(3rem, 6vw, 6rem)",
        }}
      >
        <p
          style={{
            fontSize: "clamp(1.5rem, 5.9vw, 5.9rem)",
            lineHeight: 1.15,
            letterSpacing: "-0.0475em",
            backgroundImage: "linear-gradient(93deg, rgba(255, 140, 105, 0.9) -1%, rgba(0, 136, 204, 0.7) 34%, rgba(255, 255, 255, 0.6) 85%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          No content calendar. No design tools. No agency retainers. One text. Every platform. Done.
        </p>
      </div>

      {/* CTA Button */}
      <div className="flex flex-col items-center gap-8 pb-16 md:pb-20">
        <motion.a
          href="https://t.me/ScribarioBot"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-3 font-body font-medium transition-transform duration-200 hover:scale-[1.03]"
          style={{
            backgroundColor: "var(--accent)",
            color: "#fff",
            borderRadius: 52,
            padding: "20px 40px",
            fontSize: "clamp(1rem, 1.4vw, 1.4rem)",
            letterSpacing: "-0.0175em",
            minHeight: 44,
            boxShadow: "0 8px 30px rgba(255, 107, 74, 0.25)",
          }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
          </svg>
          Text the bot now
        </motion.a>

        <motion.p
          className="font-mono"
          style={{
            fontSize: "clamp(0.7rem, 0.85vw, 0.85rem)",
            letterSpacing: "0.05em",
            color: "rgba(255,255,255,0.35)",
          }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Free to try · No signup required · Works on any phone
        </motion.p>
      </div>
    </section>
  );
}
