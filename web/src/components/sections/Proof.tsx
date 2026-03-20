"use client";

import { motion } from "framer-motion";
import { CountUp } from "@/components/ui/CountUp";
import Image from "next/image";

const stats = [
  { end: 30, suffix: "s", label: "idea to published" },
  { end: 3, suffix: "", label: "options per post" },
  { end: 5, suffix: "", label: "caption formulas" },
];

export function Proof() {
  return (
    <section
      id="proof"
      data-dark
      aria-labelledby="proof-heading"
      className="relative overflow-hidden"
      style={{
        backgroundColor: "var(--bg-dark)",
        paddingTop: "var(--section-gap)",
        paddingBottom: "var(--section-gap)",
        contain: "layout paint",
      }}
    >
      {/* Ambient glow so dark sections don't feel like black voids */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div
          className="absolute"
          style={{
            top: "10%",
            left: "20%",
            width: "60%",
            height: "50%",
            backgroundImage: "radial-gradient(ellipse 80% 60% at 50% 40%, rgba(255, 107, 74, 0.05) 0%, transparent 100%)",
          }}
        />
      </div>
      <div className="px-6 md:px-16 relative">
        {/* Section label */}
        <motion.p
          className="font-mono"
          style={{
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "rgba(255,255,255,0.4)",
            marginBottom: "clamp(1.5rem, 2vw, 2rem)",
          }}
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          The proof
        </motion.p>

        {/* Heading */}
        <motion.h2
          id="proof-heading"
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "#fff",
            marginBottom: "var(--content-gap)",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          One text.{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(166deg, rgb(255, 107, 74), rgb(255, 140, 105))",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Real post.
          </span>{" "}
          Published.
        </motion.h2>
      </div>

      {/* Browser-frame FB screenshot with glow */}
      <motion.div
        className="relative mx-auto px-6 md:px-16"
        style={{ maxWidth: 1100 }}
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, amount: 0.15 }}
        transition={{ duration: 0.8, delay: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        {/* Glow */}
        <div
          className="absolute inset-0 -z-10"
          style={{
            background: "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(255, 107, 74, 0.12) 0%, transparent 100%)",
            transform: "scale(1.2)",
          }}
        />

        {/* Browser chrome frame */}
        <div
          className="rounded-xl overflow-hidden"
          style={{
            boxShadow: "0 30px 80px -20px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.08)",
            backgroundColor: "#1a1a1e",
          }}
        >
          {/* Browser toolbar */}
          <div className="flex items-center gap-2 px-4 py-3 bg-[#1a1a1e] border-b border-white/5">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
              <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
              <div className="w-3 h-3 rounded-full bg-[#28c840]" />
            </div>
            <div className="flex-1 mx-4">
              <a
                href="https://facebook.com/scribario"
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md px-3 py-2.5 text-xs text-[#6e6e7a] bg-[#111114] truncate block hover:text-[#9e9eaa] transition-colors"
                style={{ minHeight: 44, display: "flex", alignItems: "center", fontFamily: "var(--font-mono)" }}
              >
                facebook.com/scribario
              </a>
            </div>
          </div>
          <Image
            src="/images/fb-post-proof.webp"
            alt="A real Facebook post created and published by Scribario in 30 seconds"
            width={1200}
            height={630}
            className="w-full h-auto block"
          />
        </div>
      </motion.div>

      {/* Timestamp callout */}
      <motion.div
        className="px-6 md:px-16"
        style={{ marginTop: "var(--content-gap)" }}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <p
          className="font-mono"
          style={{
            fontSize: "0.8rem",
            letterSpacing: "0.05em",
            color: "rgba(255,255,255,0.35)",
          }}
        >
          Created at 2:14pm. Live on Facebook by 2:15pm.
        </p>
      </motion.div>

      {/* Stats row */}
      <div
        className="px-6 md:px-16 grid grid-cols-3 gap-8"
        style={{
          marginTop: "var(--content-gap)",
          maxWidth: 900,
        }}
      >
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            className="text-center md:text-left"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 + i * 0.1 }}
          >
            <CountUp
              end={stat.end}
              suffix={stat.suffix}
              className="font-display font-bold"
              style={{
                fontSize: "clamp(2.5rem, 5vw, 4rem)",
                letterSpacing: "-0.04em",
                backgroundImage: "linear-gradient(135deg, rgb(255, 107, 74), rgb(255, 160, 120))",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            />
            <p
              className="font-body mt-1"
              style={{
                fontSize: "clamp(0.8rem, 1vw, 1rem)",
                color: "rgba(255,255,255,0.4)",
                letterSpacing: "-0.01em",
              }}
            >
              {stat.label}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Bottom copy */}
      <div className="px-6 md:px-16" style={{ marginTop: "var(--content-gap)" }}>
        <p
          className="font-body"
          style={{
            fontSize: "clamp(1.25rem, 2vw, 2rem)",
            lineHeight: 1.4,
            letterSpacing: "-0.01em",
            color: "rgba(255,255,255,0.45)",
            maxWidth: 600,
          }}
        >
          From Telegram message to live post in 30 seconds.
          No editing tools. No scheduling apps. Just text your bot.
        </p>
      </div>
    </section>
  );
}
