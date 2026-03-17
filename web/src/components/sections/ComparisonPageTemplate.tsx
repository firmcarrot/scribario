"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import type { ComparisonPage } from "@/content/comparisons";
import { FAQ } from "@/components/ui/FAQ";

export function ComparisonPageTemplate({ comparison }: { comparison: ComparisonPage }) {
  return (
    <>
      {/* Hero */}
      <section
        className="px-6 md:px-16"
        style={{ paddingTop: "clamp(10rem, 16vw, 16rem)", paddingBottom: "var(--section-gap)" }}
      >
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
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Compare
        </motion.p>

        <motion.h1
          className="font-display font-bold"
          style={{
            fontSize: "clamp(3rem, 6vw, 6rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            maxWidth: "18ch",
          }}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {comparison.heroHeadline}{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            {comparison.competitor}.
          </span>
        </motion.h1>

        <motion.p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
            lineHeight: 1.5,
            color: "var(--text-secondary)",
            maxWidth: "55ch",
            marginTop: "var(--item-gap)",
            letterSpacing: "-0.01em",
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {comparison.heroSubtitle}
        </motion.p>

        {/* Intro paragraphs */}
        {comparison.introparagraphs && (
          <div className="flex flex-col gap-5" style={{ marginTop: "var(--content-gap)", maxWidth: "65ch" }}>
            {comparison.introparagraphs.map((p, i) => (
              <motion.p
                key={i}
                className="font-body"
                style={{
                  fontSize: "clamp(1rem, 1.15vw, 1.15rem)",
                  lineHeight: 1.8,
                  color: "var(--text-secondary)",
                  letterSpacing: "-0.01em",
                }}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.3 + i * 0.08 }}
              >
                {p}
              </motion.p>
            ))}
          </div>
        )}
      </section>

      {/* Comparison Table */}
      <section
        style={{
          backgroundColor: "var(--bg-alt)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 max-w-[var(--max-content)] mx-auto">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 3.5vw, 3.5rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              color: "var(--text)",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Feature comparison.
          </motion.h2>

          {/* Table header */}
          <div
            className="grid grid-cols-3 gap-4 pb-4 mb-2"
            style={{ borderBottom: "2px solid rgba(0,0,0,0.1)" }}
          >
            <span className="font-mono text-xs uppercase" style={{ letterSpacing: "0.1em", color: "var(--text-secondary)" }}>
              Feature
            </span>
            <span className="font-mono text-xs uppercase" style={{ letterSpacing: "0.1em", color: "var(--accent)" }}>
              Scribario
            </span>
            <span className="font-mono text-xs uppercase" style={{ letterSpacing: "0.1em", color: "var(--text-secondary)" }}>
              {comparison.competitor}
            </span>
          </div>

          {/* Table rows */}
          {comparison.comparisonRows.map((row, i) => (
            <motion.div
              key={row.feature}
              className="grid grid-cols-3 gap-4 py-4"
              style={{
                borderBottom: "1px solid rgba(0,0,0,0.06)",
              }}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.03 }}
            >
              <span
                className="font-body font-medium"
                style={{
                  fontSize: "clamp(0.85rem, 1vw, 1rem)",
                  color: "var(--text)",
                }}
              >
                {row.feature}
              </span>
              <span
                className="font-body"
                style={{
                  fontSize: "clamp(0.85rem, 1vw, 1rem)",
                  color: "var(--text)",
                  lineHeight: 1.5,
                }}
              >
                {row.scribario}
              </span>
              <span
                className="font-body"
                style={{
                  fontSize: "clamp(0.85rem, 1vw, 1rem)",
                  color: "var(--text-secondary)",
                  lineHeight: 1.5,
                }}
              >
                {row.competitor}
              </span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Advantages */}
      <section
        style={{
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 max-w-[var(--max-content)] mx-auto">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 3.5vw, 3.5rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              color: "var(--text)",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Why switch.
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            {comparison.advantages.map((adv, i) => (
              <motion.div
                key={adv.title}
                className="flex flex-col gap-3"
                style={{
                  padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                  borderRadius: 20,
                  border: "1px solid rgba(0,0,0,0.06)",
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <h3
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                    letterSpacing: "-0.02em",
                    color: "var(--text)",
                  }}
                >
                  {adv.title}
                </h3>
                <p
                  className="font-body"
                  style={{
                    fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
                    lineHeight: 1.7,
                    color: "var(--text-secondary)",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {adv.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom Line */}
      {comparison.bottomLine && (
        <section className="px-6 md:px-16" style={{ paddingBottom: "var(--section-gap)" }}>
          <div className="max-w-[var(--max-content)] mx-auto">
            <motion.h2
              className="font-display font-bold"
              style={{
                fontSize: "clamp(1.75rem, 3vw, 3rem)",
                lineHeight: 1.1,
                letterSpacing: "-0.02em",
                color: "var(--text)",
                marginBottom: "var(--item-gap)",
              }}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              The bottom line.
            </motion.h2>
            <motion.p
              className="font-body"
              style={{
                fontSize: "clamp(1.1rem, 1.4vw, 1.4rem)",
                lineHeight: 1.7,
                color: "var(--text-secondary)",
                letterSpacing: "-0.01em",
                maxWidth: "60ch",
              }}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {comparison.bottomLine}
            </motion.p>
          </div>
        </section>
      )}

      {/* FAQ */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 max-w-[var(--max-content)] mx-auto">
          <motion.h2
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
          </motion.h2>
          <FAQ items={comparison.faq} variant="dark" />
        </div>
      </section>

      {/* CTA + Cross-links */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2.5rem, 5vw, 5rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: "#fff",
              marginBottom: "var(--item-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Ready to{" "}
            <span
              style={{
                backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              try it?
            </span>
          </motion.h2>

          <a
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
          >
            <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
            </svg>
            {comparison.ctaCopy}
          </a>

          <p
            className="font-mono mt-6"
            style={{
              fontSize: "0.75rem",
              letterSpacing: "0.05em",
              color: "rgba(255,255,255,0.3)",
            }}
          >
            Free to try · No signup required · Works on any phone
          </p>

          {/* Cross-links */}
          <div className="mt-16 pt-8" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
            <p
              className="font-mono mb-4"
              style={{
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "rgba(255,255,255,0.25)",
              }}
            >
              More comparisons
            </p>
            <div className="flex flex-wrap gap-3">
              {[
                { href: "/compare/vs-buffer", label: "vs Buffer" },
                { href: "/compare/vs-hootsuite", label: "vs Hootsuite" },
                { href: "/compare/vs-canva", label: "vs Canva" },
              ]
                .filter((l) => l.href !== `/compare/${comparison.slug}`)
                .map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="font-mono uppercase transition-all duration-150 hover:text-white"
                    style={{
                      fontSize: "0.7rem",
                      letterSpacing: "0.08em",
                      color: "rgba(255,255,255,0.35)",
                      padding: "8px 16px",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 52,
                    }}
                  >
                    {link.label} →
                  </Link>
                ))}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
