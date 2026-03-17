"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import type { NichePage } from "@/content/niches";
import { FAQ } from "@/components/ui/FAQ";

export function NichePageTemplate({ niche }: { niche: NichePage }) {
  return (
    <>
      {/* Hero — full-bleed background image, fixed parallax */}
      <section
        className="relative overflow-hidden"
        {...(niche.heroImage ? { "data-dark": true } : {})}
        aria-label={niche.heroImage ? `${niche.title} — ${niche.subtitle}` : undefined}
        style={{
          minHeight: niche.heroImage ? "clamp(600px, 80vh, 900px)" : "auto",
          paddingTop: "clamp(10rem, 16vw, 16rem)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        {/* Background image — fixed position creates parallax as content scrolls over it */}
        {niche.heroImage && (
          <>
            <div
              className="absolute inset-0 z-0"
              style={{
                backgroundImage: `url(${niche.heroImage})`,
                backgroundSize: "cover",
                backgroundPosition: "center 40%",
                backgroundRepeat: "no-repeat",
                backgroundAttachment: "fixed",
              }}
            />
            {/* Gradient overlay */}
            <div
              className="absolute inset-0 z-[1]"
              style={{
                background: `
                  linear-gradient(180deg,
                    rgba(0,0,0,0.7) 0%,
                    rgba(0,0,0,0.45) 40%,
                    rgba(0,0,0,0.55) 70%,
                    rgba(0,0,0,0.85) 100%
                  )
                `,
              }}
            />
          </>
        )}

        {/* Content — sits on top of background */}
        <div className="relative z-10 px-6 md:px-16">
          <motion.p
            className="font-mono"
            style={{
              fontSize: "0.75rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: niche.heroImage ? "rgba(255,255,255,0.5)" : "var(--text-secondary)",
              marginBottom: "clamp(1.5rem, 2vw, 2rem)",
            }}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {niche.title}
          </motion.p>

          <motion.h1
            className="font-display font-bold"
            style={{
              fontSize: "clamp(3rem, 6vw, 6rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: niche.heroImage ? "#fff" : "var(--text)",
              maxWidth: "18ch",
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            {niche.heroHeadline}{" "}
            <span
              style={{
                backgroundImage: "linear-gradient(135deg, #FF6B4A, #FFA078)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              {niche.heroAccent}
            </span>
          </motion.h1>

          <motion.p
            className="font-body"
            style={{
              fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
              lineHeight: 1.5,
              color: niche.heroImage ? "rgba(255,255,255,0.7)" : "var(--text-secondary)",
              maxWidth: "50ch",
              marginTop: "var(--item-gap)",
              letterSpacing: "-0.01em",
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {niche.subtitle}
          </motion.p>

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
              marginTop: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <TelegramIcon />
            {niche.ctaCopy}
          </motion.a>
        </div>
      </section>

      {/* Pain Points */}
      <section
        style={{
          backgroundColor: "var(--bg-alt)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 4vw, 4rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: "var(--text)",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            The problem.
          </motion.h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {niche.painPoints.map((pain, i) => (
              <motion.div
                key={pain.stat}
                className="flex flex-col gap-2"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <span
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(2rem, 4vw, 4rem)",
                    lineHeight: 1,
                    letterSpacing: "-0.03em",
                    color: "var(--accent)",
                  }}
                >
                  {pain.stat}
                </span>
                <p
                  className="font-body"
                  style={{
                    fontSize: "clamp(0.85rem, 1vw, 1rem)",
                    lineHeight: 1.5,
                    color: "var(--text-secondary)",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {pain.statement}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section
        style={{
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 4vw, 4rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: "var(--text)",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            How Scribario helps.
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            {niche.benefits.map((benefit, i) => (
              <motion.div
                key={benefit.title}
                className="flex gap-5"
                style={{
                  padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                  borderRadius: 20,
                  backgroundColor: "var(--bg)",
                  border: "1px solid rgba(0,0,0,0.06)",
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                {/* Number badge */}
                <div
                  className="shrink-0 flex items-center justify-center font-display font-bold"
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 14,
                    backgroundColor: "rgba(255, 107, 74, 0.08)",
                    color: "var(--accent)",
                    fontSize: "1.1rem",
                    letterSpacing: "-0.02em",
                  }}
                >
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div className="flex flex-col gap-3">
                  <h3
                    className="font-display font-bold"
                    style={{
                      fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                      letterSpacing: "-0.02em",
                      color: "var(--text)",
                    }}
                  >
                    {benefit.title}
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
                    {benefit.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16">
          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 4vw, 4rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: "#fff",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            What you&apos;ll post.
          </motion.h2>

          <div className="flex flex-col gap-0">
            {niche.useCases.map((uc, i) => (
              <motion.div
                key={uc.title}
                className={`flex flex-col ${uc.image ? "md:flex-row md:items-center" : ""} gap-6 md:gap-10 py-8 md:py-10`}
                style={{
                  borderBottom: i < niche.useCases.length - 1 ? "1px solid rgba(255,255,255,0.06)" : "none",
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                {/* Text side */}
                <div className="flex flex-col gap-3 flex-1">
                  <h3
                    className="font-display font-bold"
                    style={{
                      fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                      letterSpacing: "-0.02em",
                      color: "#fff",
                    }}
                  >
                    {uc.title}
                  </h3>
                  <p
                    className="font-body"
                    style={{
                      fontSize: "clamp(0.95rem, 1.1vw, 1.1rem)",
                      lineHeight: 1.6,
                      color: "rgba(255,255,255,0.5)",
                      maxWidth: "55ch",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {uc.description}
                  </p>
                  <div
                    className="font-mono"
                    style={{
                      fontSize: "0.8rem",
                      color: "var(--accent)",
                      letterSpacing: "0.02em",
                      padding: "12px 20px",
                      backgroundColor: "rgba(255, 107, 74, 0.08)",
                      borderRadius: 12,
                      border: "1px solid rgba(255, 107, 74, 0.15)",
                      maxWidth: "fit-content",
                    }}
                  >
                    {uc.example}
                  </div>
                </div>

                {/* Result image — the AI-generated post */}
                {uc.image && (
                  <div
                    className="shrink-0"
                    style={{
                      width: "clamp(220px, 28vw, 400px)",
                      aspectRatio: "1",
                      borderRadius: 20,
                      overflow: "hidden",
                      border: "1px solid rgba(255,255,255,0.1)",
                      boxShadow: "0 16px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05)",
                      transform: i % 2 === 0 ? "rotate(2deg)" : "rotate(-2deg)",
                    }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={uc.image}
                      alt={`AI-generated social media post example: ${uc.title} — created by Scribario from the prompt ${uc.example}`}
                      width={600}
                      height={600}
                      loading="lazy"
                      decoding="async"
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        display: "block",
                      }}
                    />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section
        style={{
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
              color: "var(--text)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            Questions
          </motion.h2>
          <FAQ items={niche.faq} variant="light" />
        </div>
      </section>

      {/* CTA + Cross-links */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingTop: "var(--section-gap)",
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
              start posting?
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
            <TelegramIcon />
            {niche.ctaCopy}
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

          {/* Cross-links to other niches */}
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
              Also works for
            </p>
            <div className="flex flex-wrap gap-3">
              {[
                { href: "/for/restaurants", label: "Restaurants" },
                { href: "/for/real-estate", label: "Real Estate" },
                { href: "/for/salons", label: "Salons" },
                { href: "/for/small-business", label: "Small Business" },
              ]
                .filter((l) => l.href !== `/for/${niche.slug}`)
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

function TelegramIcon() {
  return (
    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  );
}
