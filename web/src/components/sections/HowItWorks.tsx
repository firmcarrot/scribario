"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import { CountUp } from "@/components/ui/CountUp";
import Image from "next/image";

const steps = [
  { num: "01", title: "Text it", desc: "Describe what you want in plain English. No templates, no editors, no learning curve." },
  { num: "02", title: "AI creates", desc: "3 unique caption + image combos in 30 seconds. Matched to your brand voice." },
  { num: "03", title: "One tap", desc: "Approve your favorite. Published to every connected platform instantly." },
];

export function HowItWorks() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const clipRef = useRef<HTMLDivElement>(null);
  const stepRefs = useRef<(HTMLLIElement | null)[]>([]);

  useEffect(() => {
    const engine = getScrollEngine();
    const isMobile = window.innerWidth < 750;
    const startInset = isMobile ? 16 : 64;
    const startRadius = isMobile ? 24 : 45;

    let cachedCardTop = 0;
    const cachePositions = () => {
      const el = cardRef.current;
      if (el) cachedCardTop = el.getBoundingClientRect().top + window.scrollY;
    };
    cachePositions();
    setTimeout(cachePositions, 0);
    window.addEventListener("resize", cachePositions);

    engine.register("hiw-clip", (scrollY, wh) => {
      const el = cardRef.current;
      if (!el || !clipRef.current) return;

      const elTop = cachedCardTop;

      const clipStart = elTop - wh * 0.8;
      const clipEnd = elTop - wh * 0.4;
      const clipProgress = R.ease(R.iLerp(scrollY, clipStart, clipEnd));
      const insetX = R.lerp(startInset, 0, clipProgress);
      const radius = R.lerp(startRadius, 0, clipProgress);
      clipRef.current.style.clipPath = `inset(0px ${insetX}px round ${radius}px)`;

      const listStart = elTop - wh * 0.2;
      const listSpacing = wh * 0.12;
      steps.forEach((_, i) => {
        const ref = stepRefs.current[i];
        if (!ref) return;
        const itemStart = listStart + i * listSpacing;
        const itemEnd = itemStart + wh * 0.25;
        const p = R.ease(R.iLerp(scrollY, itemStart, itemEnd));
        ref.style.opacity = String(p);
        ref.style.transform = `translateY(${R.lerp(40, 0, p)}px)`;
      });
    });

    return () => {
      engine.unregister("hiw-clip");
      window.removeEventListener("resize", cachePositions);
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      aria-labelledby="hiw-heading"
      style={{ paddingTop: "var(--section-gap)", contain: "layout paint" }}
    >
      {/* Section heading — Apple-scale */}
      <motion.h2
        id="hiw-heading"
        className="font-display font-bold px-6 md:px-16"
        aria-label="How it works"
        style={{
          fontSize: "clamp(2.5rem, 5vw, 5rem)",
          lineHeight: 1.04,
          letterSpacing: "-0.03em",
          color: "var(--text)",
        }}
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6 }}
      >
        Three steps. That&apos;s it.
      </motion.h2>

      {/* Clip-path card */}
      <div ref={cardRef} className="relative" style={{ marginTop: "clamp(2rem, 4vw, 4rem)" }}>
        <div
          ref={clipRef}
          className="relative overflow-hidden"
          style={{
            clipPath: `inset(0px clamp(16px, 5vw, 64px) round clamp(24px, 3vw, 45px))`,
            willChange: "clip-path",
            backgroundColor: "var(--bg-alt)",
          }}
        >
          <div className="px-6 md:px-16 py-[8vw] md:py-[6vw]">
            {/* Animated stat */}
            <div className="mb-8 md:mb-12">
              <CountUp
                end={30}
                suffix="s"
                className="font-display font-bold"
                style={{
                  fontSize: "clamp(4rem, 8vw, 8rem)",
                  letterSpacing: "-0.04em",
                  backgroundImage: "linear-gradient(124deg, rgb(255, 107, 74) 11%, rgb(0, 136, 204) 43%, rgb(229, 85, 58) 90%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              />
              <p
                className="mt-2 font-body"
                style={{
                  fontSize: "clamp(1rem, 1.5vw, 1.5rem)",
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
              >
                Average generation time
              </p>
            </div>

            {/* Steps list */}
            <ul className="mt-12 md:mt-16 flex flex-col gap-8 md:gap-10">
              {steps.map((step, i) => (
                <li
                  key={step.num}
                  ref={(el) => { stepRefs.current[i] = el; }}
                  className="flex gap-4 md:gap-6 items-start"
                  style={{
                    opacity: 0,
                    transform: "translateY(40px)",
                    willChange: "transform, opacity",
                  }}
                >
                  <span
                    className="font-mono shrink-0"
                    style={{
                      fontSize: "clamp(0.75rem, 1vw, 1rem)",
                      color: "var(--accent)",
                      marginTop: "0.3em",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {step.num}
                  </span>
                  <div>
                    <h3
                      className="font-display font-bold"
                      style={{
                        fontSize: "clamp(1.75rem, 3vw, 3rem)",
                        letterSpacing: "-0.02em",
                        color: "var(--text)",
                      }}
                    >
                      {step.title}
                    </h3>
                    <p
                      className="mt-1 font-body"
                      style={{
                        fontSize: "clamp(0.95rem, 1.2vw, 1.2rem)",
                        color: "var(--text-secondary)",
                        letterSpacing: "-0.01em",
                        lineHeight: 1.5,
                      }}
                    >
                      {step.desc}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Comparison strip — cinematic image-driven */}
      <div
        className="px-6 md:px-16 grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8"
        style={{
          paddingTop: "var(--content-gap)",
          paddingBottom: "var(--section-gap)",
          maxWidth: "var(--max-content)",
          marginInline: "auto",
        }}
      >
        {/* Old way */}
        <motion.div
          className="rounded-2xl overflow-hidden"
          style={{
            backgroundColor: "var(--bg-dark)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="relative" style={{ aspectRatio: "16/9" }}>
            <Image
              src="/images/comparison-old-way.webp"
              alt="Cluttered desk with multiple screens, sticky notes, and design tools — the old way of managing social media"
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 50vw"
              style={{ filter: "brightness(0.85)" }}
            />
            {/* Gradient overlay at bottom for text legibility */}
            <div
              className="absolute inset-0"
              style={{
                background: "linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 50%, transparent 100%)",
              }}
            />
            <div className="absolute bottom-0 left-0 right-0 p-5 md:p-6">
              <p
                className="font-mono uppercase"
                style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: "rgba(255,255,255,0.45)", marginBottom: "0.5rem" }}
              >
                The old way
              </p>
              <p
                className="font-display font-bold"
                style={{ fontSize: "clamp(1.5rem, 2.5vw, 2.25rem)", letterSpacing: "-0.02em", color: "#fff", lineHeight: 1.15 }}
              >
                45 minutes
              </p>
            </div>
          </div>
          <div className="p-5 md:p-6">
            <div className="flex flex-col gap-2.5">
              {["Open Canva", "Write caption", "Find hashtags", "Schedule post", "Resize for each platform"].map((step, i) => (
                <div key={step} className="flex items-center gap-3">
                  <span
                    className="font-mono shrink-0"
                    style={{ fontSize: "0.7rem", color: "rgba(255,255,255,0.25)", width: 16, textAlign: "right" as const }}
                  >
                    {i + 1}.
                  </span>
                  <span
                    className="font-body"
                    style={{
                      fontSize: "0.95rem",
                      color: "rgba(255,255,255,0.5)",
                      letterSpacing: "-0.01em",
                      textDecoration: "line-through",
                      textDecorationColor: "rgba(255,255,255,0.2)",
                    }}
                  >
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Scribario way */}
        <motion.div
          className="rounded-2xl overflow-hidden"
          style={{
            backgroundColor: "#fff",
            boxShadow: "0 20px 60px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04)",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15 }}
        >
          <div className="relative" style={{ aspectRatio: "16/9" }}>
            <Image
              src="/images/comparison-scribario.webp"
              alt="Clean desk with just a phone showing a single Telegram message and a cup of coffee — the Scribario way"
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 50vw"
            />
            <div
              className="absolute inset-0"
              style={{
                background: "linear-gradient(0deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.05) 50%, transparent 100%)",
              }}
            />
            <div className="absolute bottom-0 left-0 right-0 p-5 md:p-6">
              <p
                className="font-mono uppercase"
                style={{ fontSize: "0.65rem", letterSpacing: "0.12em", color: "rgba(255,255,255,0.6)", marginBottom: "0.5rem" }}
              >
                Scribario
              </p>
              <p
                className="font-display font-bold"
                style={{
                  fontSize: "clamp(1.5rem, 2.5vw, 2.25rem)",
                  letterSpacing: "-0.02em",
                  lineHeight: 1.15,
                  backgroundImage: "linear-gradient(135deg, rgb(255, 107, 74), rgb(255, 180, 140))",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                30 seconds
              </p>
            </div>
          </div>
          <div className="p-5 md:p-6">
            <div className="flex items-center gap-3">
              <span style={{ color: "var(--accent)", fontSize: "1.1rem", fontWeight: 600 }}>→</span>
              <span
                className="font-body"
                style={{ fontSize: "0.95rem", color: "var(--text)", letterSpacing: "-0.01em" }}
              >
                Text your idea to Telegram
              </span>
            </div>
            <p
              className="font-body mt-4"
              style={{
                fontSize: "0.85rem",
                color: "var(--text-secondary)",
                letterSpacing: "-0.01em",
                lineHeight: 1.6,
              }}
            >
              One message. Three publish-ready options. Posted everywhere.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
