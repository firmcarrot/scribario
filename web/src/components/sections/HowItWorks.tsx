"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import { CountUp } from "@/components/ui/CountUp";

const steps = [
  { num: "01", title: "Text it", desc: "Describe what you want in plain English. No templates, no editors." },
  { num: "02", title: "AI creates", desc: "3 unique caption + image combos in 30 seconds. Matched to your brand." },
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

    // Cache element position — use getBoundingClientRect + scrollY for accuracy
    // (offsetTop is wrong when contain: layout paint shifts offsetParent)
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

      // List stagger — direct DOM write
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
      style={{ marginTop: "clamp(6rem, 17.36vw, 17.36rem)", contain: "layout paint" }}
    >
      {/* Massive section heading */}
      <motion.h2
        id="hiw-heading"
        className="font-display font-bold px-6 md:px-16"
        aria-label="How it works"
        style={{
          fontSize: "clamp(3rem, 15vw, 15rem)",
          lineHeight: 1,
          letterSpacing: "-0.0575em",
          color: "var(--text)",
        }}
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6 }}
      >
        <span className="block">How it</span>
        <span className="block">works</span>
      </motion.h2>

      {/* Clip-path card */}
      <div ref={cardRef} className="relative" style={{ marginTop: "4vw" }}>
        <div
          ref={clipRef}
          className="relative overflow-hidden"
          style={{
            clipPath: `inset(0px 64px round 45px)`,
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
                className="font-display font-bold text-[clamp(4rem,8vw,8rem)]"
                style={{
                  backgroundImage: "linear-gradient(124deg, rgb(255, 107, 74) 11%, rgb(0, 136, 204) 43%, rgb(229, 85, 58) 90%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              />
              <p
                className="mt-2"
                style={{
                  fontSize: "clamp(1rem, 1.8vw, 1.8rem)",
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.0475em",
                }}
              >
                Average generation time
              </p>
            </div>

            {/* Intro text */}
            <p
              style={{
                fontSize: "clamp(1.25rem, 3.05vw, 3.05rem)",
                lineHeight: 1.18,
                letterSpacing: "-0.0475em",
                color: "rgba(0,0,0,0.82)",
              }}
            >
              Three steps between your idea and a{" "}
              <span
                style={{
                  backgroundImage: "linear-gradient(244deg, rgb(255, 107, 74) 17%, rgb(255, 140, 105) 61%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                published post
              </span>
              .
            </p>

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
                      fontSize: "clamp(0.75rem, 1.2vw, 1.2rem)",
                      color: "var(--accent)",
                      marginTop: "0.3em",
                    }}
                  >
                    {step.num}
                  </span>
                  <div>
                    <h3
                      className="font-display font-bold"
                      style={{
                        fontSize: "clamp(1.25rem, 2.4vw, 2.4rem)",
                        letterSpacing: "-0.0475em",
                        color: "var(--text)",
                      }}
                    >
                      {step.title}
                    </h3>
                    <p
                      className="mt-1"
                      style={{
                        fontSize: "clamp(0.875rem, 1.5vw, 1.5rem)",
                        color: "var(--text-secondary)",
                        letterSpacing: "-0.0475em",
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

      {/* Section copy — gradient text */}
      <div
        className="px-[clamp(2rem,10.83vw,10.83rem)]"
        style={{
          paddingTop: "clamp(4rem, 11.11vw, 11.11rem)",
          paddingBottom: "clamp(6rem, 17.36vw, 17.36rem)",
        }}
      >
        <p
          style={{
            fontSize: "clamp(1.5rem, 5.9vw, 5.9rem)",
            lineHeight: 1.15,
            letterSpacing: "-0.0475em",
            backgroundImage: "linear-gradient(124deg, rgb(255, 107, 74) 11%, rgb(0, 136, 204) 43%, rgb(0, 0, 0) 90%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          One message. Three options. Every platform. That&apos;s the whole workflow.
        </p>
      </div>
    </section>
  );
}
