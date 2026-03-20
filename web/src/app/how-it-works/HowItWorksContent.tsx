"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { FAQ } from "@/components/ui/FAQ";

const steps = [
  {
    number: "01",
    title: "Open Telegram. Text your idea.",
    detail:
      "Search @ScribarioBot in Telegram and start a conversation. Describe what you want to post — \"promote our weekend brunch special\" or \"announce our new listing at 123 Oak St.\" No templates, no forms, no creative brief. Just talk.",
    example: "\"Post about our new summer cocktail menu with happy hour pricing\"",
    imageSrc: "/images/hiw-step1.webp",
    imageAlt: "Hands holding a smartphone typing a Telegram message in a warm café — Scribario social media automation starts with a text",
  },
  {
    number: "02",
    title: "Get three unique options.",
    detail:
      "Scribario's AI analyzes your request and creates three completely different caption-and-image combinations. Each uses a different writing formula — a hook story, a punchy one-liner, a value-driven list — so you're choosing between genuinely different approaches, not minor variations.",
    example: "Three cards appear with preview images and caption text. Tap any to preview full-size.",
    imageSrc: "/images/hiw-step2.webp",
    imageAlt: "Phone screen showing three AI-generated social media post options with captions and images — Scribario creates multiple unique options",
  },
  {
    number: "03",
    title: "Edit, refine, or approve.",
    detail:
      "Love one? Tap Approve. Want changes? Tap Edit and describe what you want — \"make it shorter,\" \"change the tone to playful,\" \"regenerate just the image.\" The AI revises while keeping your brand voice. Iterate until it's perfect.",
    example: "\"Make option 2 shorter and add a question hook at the beginning\"",
    imageSrc: "/images/hiw-step3.webp",
    imageAlt: "Before and after comparison of a social media caption being refined with natural language editing — Scribario AI caption editing",
  },
  {
    number: "04",
    title: "Published everywhere. Done.",
    detail:
      "One tap publishes to Facebook — with more platforms coming soon. Each post is formatted for the platform's requirements. Want to schedule it? Just say \"post this Friday at 9am.\" Or set up Autopilot and let Scribario post on a schedule automatically.",
    example: "\"Post to Facebook, schedule for tomorrow at noon\"",
    imageSrc: "/images/hiw-step4.webp",
    imageAlt: "Phone on desk showing a published Facebook post — Scribario publishes with one tap",
  },
];

const comparisons = [
  { label: "Open Canva", time: "2 min" },
  { label: "Pick a template", time: "3 min" },
  { label: "Customize design", time: "10 min" },
  { label: "Write caption", time: "8 min" },
  { label: "Find hashtags", time: "5 min" },
  { label: "Resize for each platform", time: "5 min" },
  { label: "Open scheduler", time: "2 min" },
  { label: "Upload & schedule", time: "5 min" },
];

const faqItems = [
  {
    question: "How long does it really take?",
    answer:
      "From text to published post: 30 seconds if you approve the first option. 1-2 minutes if you want to edit or iterate. Compare that to the 40+ minute workflow most people use with design tools and schedulers.",
  },
  {
    question: "Do I need to download an app?",
    answer:
      "No. Telegram is available on iOS, Android, Windows, Mac, and Linux. If you already have Telegram, you can start using Scribario in 10 seconds. If not, download Telegram (free) and search for @ScribarioBot.",
  },
  {
    question: "What if my brand voice changes over time?",
    answer:
      "Scribario learns from every post you approve. As your voice evolves, the AI adapts. You can also update your brand profile anytime with /brand — change your tone, audience, or content preferences.",
  },
  {
    question: "Can I manage multiple brands?",
    answer:
      "Yes, on the Pro plan. Each brand has its own voice profile, style settings, and connected platforms. Switch between brands within the same Telegram conversation.",
  },
  {
    question: "What happens if I don't like any of the three options?",
    answer:
      "Tap Regenerate to get three entirely new options. Or edit any option with specific feedback — \"more formal,\" \"add a call-to-action,\" \"different image style.\" You're never stuck with what the AI gives you first.",
  },
];

export function HowItWorksContent() {
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
          How It Works
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
          Text it.{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Post it.
          </span>
        </motion.h1>

        <motion.p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
            lineHeight: 1.5,
            color: "var(--text-secondary)",
            maxWidth: "50ch",
            marginTop: "var(--item-gap)",
            letterSpacing: "-0.01em",
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          Four steps. No design skills. No content calendar. No agency.
          Just you, Telegram, and AI that actually gets it.
        </motion.p>
      </section>

      {/* Steps */}
      <section
        style={{
          backgroundColor: "var(--bg-alt)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 max-w-[var(--max-content)] mx-auto">
          <div className="flex flex-col gap-0">
            {steps.map((step, i) => {
              const isEven = i % 2 === 0;
              return (
                <motion.div
                  key={step.number}
                  className={`flex flex-col ${isEven ? "md:flex-row" : "md:flex-row-reverse"} md:gap-12 items-start md:items-center py-10 md:py-14`}
                  style={{
                    borderBottom: i < steps.length - 1 ? "1px solid rgba(0,0,0,0.06)" : "none",
                  }}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                >
                  {/* Image */}
                  <motion.div
                    className="w-full md:w-5/12 shrink-0 mb-6 md:mb-0"
                    whileHover={{ y: -8, scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  >
                    <div
                      className="relative overflow-hidden rounded-2xl transition-shadow duration-300"
                      style={{
                        aspectRatio: "1/1",
                        boxShadow: "0 25px 60px -10px rgba(0,0,0,0.15), 0 12px 25px -8px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.04)",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = "0 35px 80px -10px rgba(0,0,0,0.2), 0 20px 40px -10px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.04)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = "0 25px 60px -10px rgba(0,0,0,0.15), 0 12px 25px -8px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.04)";
                      }}
                    >
                      <Image
                        src={step.imageSrc}
                        alt={step.imageAlt}
                        fill
                        className="object-cover transition-transform duration-500 hover:scale-105"
                        sizes="(max-width: 768px) 100vw, 42vw"
                        loading="lazy"
                      />
                    </div>
                  </motion.div>

                  {/* Content */}
                  <div className="flex flex-col gap-4 flex-1">
                    <span
                      className="font-display font-bold"
                      style={{
                        fontSize: "clamp(3rem, 5vw, 5rem)",
                        lineHeight: 1,
                        letterSpacing: "-0.04em",
                        color: "rgba(0,0,0,0.06)",
                      }}
                    >
                      {step.number}
                    </span>
                    <h2
                      className="font-display font-bold"
                      style={{
                        fontSize: "clamp(1.75rem, 3vw, 3rem)",
                        lineHeight: 1.1,
                        letterSpacing: "-0.02em",
                        color: "var(--text)",
                      }}
                    >
                      {step.title}
                    </h2>
                    <p
                      className="font-body"
                      style={{
                        fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
                        lineHeight: 1.7,
                        color: "var(--text-secondary)",
                        maxWidth: "55ch",
                        letterSpacing: "-0.01em",
                      }}
                    >
                      {step.detail}
                    </p>
                    <div
                      className="font-mono"
                      style={{
                        fontSize: "0.8rem",
                        color: "var(--accent)",
                        letterSpacing: "0.02em",
                        padding: "12px 20px",
                        backgroundColor: "rgba(255, 107, 74, 0.06)",
                        borderRadius: 12,
                        border: "1px solid rgba(255, 107, 74, 0.1)",
                        maxWidth: "fit-content",
                      }}
                    >
                      {step.example}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Comparison: Old Way vs Scribario */}
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
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2rem, 4vw, 4rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              color: "#fff",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            The old way vs.{" "}
            <span
              style={{
                backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Scribario.
            </span>
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12">
            {/* Old Way */}
            <motion.div
              className="flex flex-col gap-0"
              style={{
                padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                borderRadius: 20,
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <p
                className="font-mono"
                style={{
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "rgba(255,255,255,0.3)",
                  marginBottom: 24,
                }}
              >
                Traditional workflow
              </p>
              {comparisons.map((c, i) => (
                <div
                  key={c.label}
                  className="flex items-center justify-between py-3"
                  style={{
                    borderBottom: i < comparisons.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none",
                  }}
                >
                  <span
                    className="font-body"
                    style={{
                      fontSize: "0.9rem",
                      color: "rgba(255,255,255,0.5)",
                      textDecoration: "line-through",
                      textDecorationColor: "rgba(255,255,255,0.2)",
                    }}
                  >
                    {c.label}
                  </span>
                  <span
                    className="font-mono"
                    style={{
                      fontSize: "0.75rem",
                      color: "rgba(255,255,255,0.3)",
                    }}
                  >
                    {c.time}
                  </span>
                </div>
              ))}
              <div
                className="flex items-center justify-between pt-5 mt-3"
                style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}
              >
                <span className="font-body font-medium" style={{ color: "rgba(255,255,255,0.7)" }}>
                  Total
                </span>
                <span
                  className="font-display font-bold"
                  style={{ fontSize: "1.5rem", color: "rgba(255,255,255,0.7)" }}
                >
                  40 min
                </span>
              </div>
            </motion.div>

            {/* Scribario Way */}
            <motion.div
              className="flex flex-col justify-between"
              style={{
                padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                borderRadius: 20,
                backgroundColor: "rgba(255, 107, 74, 0.06)",
                border: "1px solid rgba(255, 107, 74, 0.15)",
              }}
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div>
                <p
                  className="font-mono"
                  style={{
                    fontSize: "0.7rem",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: "var(--accent)",
                    marginBottom: 24,
                  }}
                >
                  Scribario
                </p>

                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-3">
                    <span style={{ color: "var(--accent)" }}>1.</span>
                    <span className="font-body" style={{ color: "rgba(255,255,255,0.8)", fontSize: "1rem" }}>
                      Text your idea
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span style={{ color: "var(--accent)" }}>2.</span>
                    <span className="font-body" style={{ color: "rgba(255,255,255,0.8)", fontSize: "1rem" }}>
                      Pick your favorite
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span style={{ color: "var(--accent)" }}>3.</span>
                    <span className="font-body" style={{ color: "rgba(255,255,255,0.8)", fontSize: "1rem" }}>
                      Tap Approve
                    </span>
                  </div>
                </div>
              </div>

              <div
                className="flex items-center justify-between pt-5 mt-8"
                style={{ borderTop: "1px solid rgba(255, 107, 74, 0.2)" }}
              >
                <span className="font-body font-medium" style={{ color: "#fff" }}>
                  Total
                </span>
                <span
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(3rem, 5vw, 5rem)",
                    letterSpacing: "-0.03em",
                    backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
                    backgroundClip: "text",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  30s
                </span>
              </div>
            </motion.div>
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
          <FAQ items={faqItems} variant="light" />
        </div>
      </section>

      {/* CTA */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 text-center">
          <motion.h2
            className="font-display font-bold mx-auto"
            style={{
              fontSize: "clamp(2.5rem, 5vw, 5rem)",
              lineHeight: 1.04,
              letterSpacing: "-0.03em",
              color: "#fff",
              maxWidth: "16ch",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Ready to try it?
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
            Start posting in 30 seconds
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
        </div>
      </section>
    </>
  );
}
