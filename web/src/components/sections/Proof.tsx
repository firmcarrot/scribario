"use client";

import { motion } from "framer-motion";
import Image from "next/image";

export function Proof() {
  return (
    <section
      id="proof"
      data-dark
      aria-labelledby="proof-heading"
      style={{
        backgroundColor: "var(--bg-dark)",
        paddingTop: "clamp(4rem, 11.11vw, 11.11rem)",
        paddingBottom: "clamp(6rem, 17.36vw, 17.36rem)",
        contain: "layout paint",
      }}
    >
      <div className="px-6 md:px-16">
        {/* Section label */}
        <motion.p
          className="font-mono text-sm uppercase tracking-widest mb-6"
          style={{ color: "rgba(255,255,255,0.55)" }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          The result
        </motion.p>

        {/* Heading */}
        <motion.h2
          id="proof-heading"
          className="font-display font-bold mb-16 md:mb-20"
          style={{
            fontSize: "clamp(2rem, 5.625vw, 5.625rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.0575em",
            color: "#fff",
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
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.15 }}
        transition={{ duration: 0.8, delay: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        {/* Glow behind the screenshot */}
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
            backgroundColor: "#2a2a2e",
          }}
        >
          {/* Browser toolbar */}
          <div className="flex items-center gap-2 px-4 py-3 bg-[#2a2a2e] border-b border-white/5">
            {/* Traffic lights */}
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
              <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
              <div className="w-3 h-3 rounded-full bg-[#28c840]" />
            </div>
            {/* URL bar */}
            <div className="flex-1 mx-4">
              <a
                href="https://facebook.com/scribario"
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md px-3 py-2.5 text-xs text-[#8e8e9a] bg-[#1e1e22] truncate block hover:text-[#b0b0bc] transition-colors"
                style={{ minHeight: 44, display: "flex", alignItems: "center", fontFamily: "var(--font-mono)" }}
              >
                facebook.com/scribario
              </a>
            </div>
          </div>
          {/* Screenshot */}
          <Image
            src="/images/fb-post-proof.webp"
            alt="A real Facebook post created and published by Scribario in 30 seconds"
            width={1200}
            height={630}
            className="w-full h-auto block"
          />
        </div>
      </motion.div>

      {/* Bottom copy */}
      <div className="px-6 md:px-16 mt-16 md:mt-20">
        <p
          className="font-body"
          style={{
            fontSize: "clamp(1.25rem, 2.4vw, 2.4rem)",
            lineHeight: 1.4,
            letterSpacing: "-0.0475em",
            color: "rgba(255,255,255,0.5)",
            maxWidth: 600,
          }}
        >
          30 seconds from Telegram message to live Facebook post.
          No editing tools. No scheduling apps. Just text your bot.
        </p>
      </div>
    </section>
  );
}
