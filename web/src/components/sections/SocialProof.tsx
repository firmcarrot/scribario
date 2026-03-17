"use client";

import { motion } from "framer-motion";
import { CountUp } from "@/components/ui/CountUp";

const stats = [
  { end: 47000, suffix: "+", label: "Posts generated", description: "and counting" },
  { end: 9, suffix: "", label: "Platforms", description: "connected" },
  { end: 30, suffix: "s", label: "Average time", description: "idea to published" },
  { end: 5, suffix: "", label: "Caption formulas", description: "matched to your voice" },
];

export function SocialProof() {
  return (
    <section
      id="social-proof"
      aria-labelledby="proof-stats-heading"
      style={{
        paddingTop: "var(--section-gap)",
        paddingBottom: "var(--section-gap)",
      }}
    >
      <div style={{ maxWidth: "var(--max-content)", marginInline: "auto", paddingInline: "var(--side-padding)" }}>
        <motion.p
          className="font-mono"
          style={{
            fontSize: "0.75rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--text-secondary)",
            marginBottom: "clamp(1.5rem, 2vw, 2rem)",
          }}
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          By the numbers
        </motion.p>

        <motion.h2
          id="proof-stats-heading"
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            maxWidth: "14ch",
            marginBottom: "var(--content-gap)",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Built for speed. Proven at scale.
        </motion.h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-y-10 gap-x-6 md:gap-12">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 + i * 0.08 }}
            >
              <CountUp
                end={stat.end}
                suffix={stat.suffix}
                className="font-display font-bold block"
                style={{
                  fontSize: "clamp(2.25rem, 5vw, 5rem)",
                  letterSpacing: "-0.04em",
                  color: "var(--text)",
                  lineHeight: 1,
                }}
              />
              <p
                className="font-display font-bold mt-2"
                style={{
                  fontSize: "clamp(0.9rem, 1.1vw, 1.1rem)",
                  letterSpacing: "-0.01em",
                  color: "var(--text)",
                }}
              >
                {stat.label}
              </p>
              <p
                className="font-body mt-1"
                style={{
                  fontSize: "clamp(0.8rem, 0.9vw, 0.9rem)",
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
              >
                {stat.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
