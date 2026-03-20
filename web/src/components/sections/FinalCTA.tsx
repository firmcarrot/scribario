"use client";

import { useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { getScrollEngine, R } from "@/lib/scroll-engine";
import { FAQ } from "@/components/ui/FAQ";
import { EmailCapture } from "@/components/ui/EmailCapture";
import Image from "next/image";

const faqItems = [
  {
    question: "Is Scribario free to try?",
    answer: "Yes. Open Telegram, search @ScribarioBot, and start texting. No signup, no credit card. You can create posts immediately and see exactly what you'll get before connecting any platforms.",
  },
  {
    question: "Do I need to know anything about social media?",
    answer: "No. Just describe what you want to post in plain English — 'promote our weekend brunch special' or 'announce our new listing at 123 Oak St.' Scribario handles the caption writing, image creation, hashtags, and formatting for each platform.",
  },
  {
    question: "Which platforms does it publish to?",
    answer: "Facebook is fully connected right now. More platforms — Instagram, LinkedIn, X, TikTok, and others — are coming soon.",
  },
  {
    question: "How is this different from Buffer or Hootsuite?",
    answer: "Those tools are dashboards that help you schedule content you've already created. Scribario creates the content for you — captions, images, video — and publishes it. There's no dashboard to learn. The entire workflow happens in a text conversation.",
  },
  {
    question: "Can it match my brand's voice and style?",
    answer: "Yes. Scribario learns from every post you approve. The more you use it, the better it understands your tone, vocabulary, and style preferences. You can also upload reference photos so your visuals stay consistent.",
  },
  {
    question: "What about video content?",
    answer: "Scribario generates short-form video clips (5-10 seconds) with AI. Just describe the video you want — same text conversation, same 30-second workflow. Available as an add-on on all paid plans.",
  },
  {
    question: "Can I manage my social media from Telegram?",
    answer: "That's the entire idea. Telegram is your interface — no app to download, no dashboard to learn. Text your bot, approve the content, and it's published. You can do it from your phone while standing in line at the grocery store.",
  },
  {
    question: "What if I don't like the options?",
    answer: "Tap Edit and describe what you want changed — 'make it shorter,' 'add a question hook,' 'more professional tone.' You can also regenerate just one image without losing the caption you liked. Iterate until it's perfect.",
  },
];

export function FinalCTA() {
  const sectionRef = useRef<HTMLElement>(null);
  const phoneSectionRef = useRef<HTMLDivElement>(null);
  const phoneWrapperRef = useRef<HTMLDivElement>(null);
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
        pw.style.transform = `perspective(1200px) rotateX(${rotateX}deg) scale(${scale})`;
        pw.style.opacity = String(p);
      }
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
      {/* DESKTOP: Sticky phone scroll zone */}
      <div
        ref={phoneSectionRef}
        className="relative hidden md:block"
        style={{ height: "150vh" }}
      >
        <div className="sticky top-[5vh] z-20" style={{ perspective: "1200px" }}>
          <div
            ref={phoneWrapperRef}
            className="flex justify-center"
            style={{
              transform: "perspective(1200px) rotateX(15deg) scale(0.85)",
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
                style={{ filter: "drop-shadow(0 40px 100px rgba(0,0,0,0.5))" }}
              />
            </div>
          </div>
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
      </div>

      {/* Massive heading */}
      <div className="px-6 md:px-16" style={{ paddingTop: "var(--content-gap)" }}>
        <motion.h2
          id="final-cta-heading"
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "#fff",
          }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          Stop scrolling.{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, rgb(255, 107, 74), rgb(255, 160, 120))",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Start posting.
          </span>
        </motion.h2>
      </div>

      {/* Body copy */}
      <div className="px-6 md:px-16" style={{ paddingTop: "var(--item-gap)" }}>
        <p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
            lineHeight: 1.5,
            color: "rgba(255,255,255,0.5)",
            maxWidth: "50ch",
            letterSpacing: "-0.01em",
          }}
        >
          No content calendar. No design tools. No agency retainers.
          One text. Published. Done.
        </p>
      </div>

      {/* CTA */}
      <div className="flex flex-col items-start gap-6 px-6 md:px-16" style={{ paddingTop: "var(--content-gap)" }}>
        <motion.a
          href="https://t.me/ScribarioBot"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-3 font-body font-medium transition-all duration-200 hover:scale-[1.02]"
          style={{
            backgroundColor: "var(--accent)",
            color: "#fff",
            borderRadius: 52,
            padding: "18px 36px",
            fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
            letterSpacing: "-0.01em",
            minHeight: 48,
            boxShadow: "0 8px 30px rgba(255, 107, 74, 0.3)",
          }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
          </svg>
          Try it free on Telegram
        </motion.a>

        <motion.p
          className="font-mono"
          style={{
            fontSize: "0.75rem",
            letterSpacing: "0.05em",
            color: "rgba(255,255,255,0.3)",
          }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Free to try · No signup required · Works on any phone
        </motion.p>
      </div>

      {/* Email capture alternative */}
      <div className="px-6 md:px-16 flex justify-start" style={{ paddingTop: "var(--content-gap)" }}>
        <EmailCapture
          headline="Not ready? Get a 3-minute demo video in your inbox."
          buttonText="Send it"
          source="final-cta"
          variant="dark"
        />
      </div>

      {/* FAQ */}
      <div className="px-6 md:px-16" style={{ paddingTop: "var(--section-gap)", paddingBottom: "var(--section-gap)" }}>
        <motion.h3
          className="font-display font-bold mb-8"
          style={{
            fontSize: "clamp(1.75rem, 3vw, 3rem)",
            letterSpacing: "-0.02em",
            color: "#fff",
          }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Questions
        </motion.h3>
        <FAQ items={faqItems} variant="dark" />
      </div>
    </section>
  );
}
