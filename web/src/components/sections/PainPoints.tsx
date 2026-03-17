"use client";

import { motion } from "framer-motion";

const pains = [
  {
    stat: "3hrs",
    label: "per day",
    headline: "You didn't start a business to manage social media.",
    body: "Content calendars, caption writing, image editing, scheduling tools — you're spending half your workday on posts instead of running your business.",
  },
  {
    stat: "$2K+",
    label: "per month",
    headline: "Agencies charge a fortune for what takes you 30 seconds.",
    body: "Social media managers and agencies cost thousands. For most small businesses, that's more than the revenue those posts even generate.",
  },
  {
    stat: "4",
    label: "subscriptions",
    headline: "You need four tools just to publish one post.",
    body: "Canva for images. ChatGPT for captions. Buffer for scheduling. Hashtag generators for reach. That's four tabs, four logins, four invoices.",
  },
  {
    stat: "0",
    label: "personality",
    headline: "Templates make your brand look like everyone else's.",
    body: "Cookie-cutter designs and generic AI captions strip away everything that makes your business unique. Your customers can tell.",
  },
];

export function PainPoints() {
  return (
    <section
      id="pain-points"
      aria-labelledby="pain-heading"
      style={{
        paddingTop: "var(--section-gap)",
        paddingBottom: "var(--section-gap)",
      }}
    >
      <div style={{ maxWidth: "var(--max-content)", marginInline: "auto", paddingInline: "var(--side-padding)" }}>
        {/* Section label */}
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
          The problem
        </motion.p>

        {/* Section heading */}
        <motion.h2
          id="pain-heading"
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            maxWidth: "18ch",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Social media is broken for small business.
        </motion.h2>

        {/* Pain cards — 2x2 grid on desktop, stacked on mobile */}
        <div
          className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12"
          style={{ marginTop: "var(--content-gap)" }}
        >
          {pains.map((pain, i) => (
            <motion.div
              key={pain.headline}
              className="flex flex-col gap-4"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 + i * 0.08 }}
            >
              {/* Stat */}
              <div className="flex items-baseline gap-2">
                <span
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(2.5rem, 4vw, 4rem)",
                    letterSpacing: "-0.04em",
                    color: "var(--accent)",
                    lineHeight: 1,
                  }}
                >
                  {pain.stat}
                </span>
                <span
                  className="font-mono uppercase"
                  style={{
                    fontSize: "0.7rem",
                    letterSpacing: "0.08em",
                    color: "var(--text-secondary)",
                  }}
                >
                  {pain.label}
                </span>
              </div>

              {/* Headline */}
              <h3
                className="font-display font-bold"
                style={{
                  fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                  lineHeight: 1.2,
                  letterSpacing: "-0.02em",
                  color: "var(--text)",
                }}
              >
                {pain.headline}
              </h3>

              {/* Body */}
              <p
                className="font-body"
                style={{
                  fontSize: "clamp(0.95rem, 1.1vw, 1.1rem)",
                  lineHeight: 1.6,
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
              >
                {pain.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
