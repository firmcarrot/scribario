"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const milestones = [
  { label: "Idea", detail: "What if social media took 30 seconds instead of 3 hours?" },
  { label: "Prototype", detail: "First Telegram bot generates AI-powered captions" },
  { label: "Image Gen", detail: "AI image generation — matched to every post automatically" },
  { label: "Facebook Live", detail: "First platform fully connected — more coming soon" },
  { label: "Video", detail: "AI video generation with voiceover, SFX, and logo watermarks" },
  { label: "Brand Voice", detail: "System learns your tone from every approved post" },
];

const techStack = [
  { name: "AI Text Engine", role: "Caption writing, conversation understanding, brand voice matching" },
  { name: "AI Image Engine", role: "Image generation — photorealistic, cinematic, watercolor, cartoon" },
  { name: "AI Video Engine", role: "Short-form video generation (5-10 second clips)" },
  { name: "AI Voice Engine", role: "Natural voiceover for video content" },
  { name: "Telegram", role: "Your interface — no app to download, no dashboard to learn" },
];

export function AboutContent() {
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
          About
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
          Social media should take{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            30 seconds.
          </span>
        </motion.h1>

        <motion.p
          className="font-body"
          style={{
            fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
            lineHeight: 1.6,
            color: "var(--text-secondary)",
            maxWidth: "55ch",
            marginTop: "var(--item-gap)",
            letterSpacing: "-0.01em",
          }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          Not 3 hours. Not $2,000/month. Not four different apps.
          Just a text message — and your social media is done.
        </motion.p>
      </section>

      {/* The Problem */}
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
            The problem we&apos;re solving
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12">
            {[
              {
                title: "Small businesses need social media to survive.",
                body: "But the people running these businesses — restaurant owners, salon operators, real estate agents, shop owners — didn't start their business to become content creators. They started it to serve customers.",
              },
              {
                title: "The industry's solution is complexity.",
                body: "Content calendars. Design tools. Scheduling platforms. Analytics dashboards. Agency retainers. The social media industry has created an entire ecosystem of tools that assumes you have a marketing team. Most small businesses don't.",
              },
              {
                title: "Templates make you look like everyone else.",
                body: "Canva templates are recognizable from a mile away. When your salon post looks identical to every other salon on Instagram, you're invisible. AI-generated original content doesn't have this problem.",
              },
              {
                title: "The cost doesn't scale down.",
                body: "Agencies charge $1,500–$3,000/month whether you're a Fortune 500 or a taco truck. Buffer, Hootsuite, Later, Sprout Social — they're all priced for teams, not solopreneurs. The tools designed for big companies don't work for small ones.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                className="flex flex-col gap-3"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <h3
                  className="font-display font-bold"
                  style={{
                    fontSize: "clamp(1.15rem, 1.5vw, 1.5rem)",
                    letterSpacing: "-0.02em",
                    color: "var(--text)",
                  }}
                >
                  {item.title}
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
                  {item.body}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Answer */}
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
              fontSize: "clamp(2rem, 3.5vw, 3.5rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              color: "#fff",
              marginBottom: "var(--item-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Our answer: make the interface disappear.
          </motion.h2>

          <motion.p
            className="font-body"
            style={{
              fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
              lineHeight: 1.6,
              color: "rgba(255,255,255,0.6)",
              maxWidth: "60ch",
              letterSpacing: "-0.01em",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Scribario lives inside Telegram — an app you already have on your phone.
            There&apos;s no dashboard to learn, no design tool to master, no scheduling
            calendar to maintain. You text what you want to post, and the AI creates
            three publish-ready options with captions, images, and platform-specific
            formatting. Approve one, and it&apos;s live on Facebook in seconds.
          </motion.p>

          <motion.p
            className="font-body"
            style={{
              fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
              lineHeight: 1.6,
              color: "rgba(255,255,255,0.6)",
              maxWidth: "60ch",
              letterSpacing: "-0.01em",
            }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            The entire workflow — from idea to published post — takes less time than
            it takes to open Canva. That&apos;s not a feature. That&apos;s the whole point.
          </motion.p>
        </div>
      </section>

      {/* Technology */}
      <section
        style={{
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16 max-w-[var(--max-content)] mx-auto">
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
            Technology
          </motion.p>

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
            Built on the best AI, not one-size-fits-all.
          </motion.h2>

          <p
            className="font-body"
            style={{
              fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
              lineHeight: 1.6,
              color: "var(--text-secondary)",
              maxWidth: "55ch",
              letterSpacing: "-0.01em",
              marginBottom: "var(--content-gap)",
            }}
          >
            Most AI tools use a single model for everything. Scribario uses specialized
            AI for each task — the best caption writer, the best image generator, the best
            video engine — orchestrated into a single conversation.
          </p>

          <div className="flex flex-col gap-0">
            {techStack.map((tech, i) => (
              <motion.div
                key={tech.name}
                className="flex flex-col md:flex-row md:items-center md:gap-8 py-5"
                style={{ borderBottom: "1px solid var(--separator)" }}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
              >
                <span
                  className="font-display font-bold shrink-0"
                  style={{
                    fontSize: "clamp(1.1rem, 1.4vw, 1.4rem)",
                    letterSpacing: "-0.02em",
                    color: "var(--text)",
                    width: 200,
                  }}
                >
                  {tech.name}
                </span>
                <span
                  className="font-body"
                  style={{
                    fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
                    color: "var(--text-secondary)",
                    lineHeight: 1.6,
                    letterSpacing: "-0.01em",
                  }}
                >
                  {tech.role}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
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
            How we got here
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {milestones.map((ms, i) => (
              <motion.div
                key={ms.label}
                className="flex flex-col gap-2"
                style={{
                  padding: "clamp(1.5rem, 2vw, 2rem)",
                  borderRadius: 16,
                  backgroundColor: "#fff",
                  border: "1px solid rgba(0,0,0,0.06)",
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
              >
                <span
                  className="font-mono"
                  style={{
                    fontSize: "0.7rem",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: "var(--accent)",
                  }}
                >
                  {ms.label}
                </span>
                <p
                  className="font-body"
                  style={{
                    fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
                    lineHeight: 1.6,
                    color: "var(--text-secondary)",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {ms.detail}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact / CTA */}
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
            Want to talk?
          </motion.h2>
          <motion.p
            className="font-body"
            style={{
              fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
              lineHeight: 1.6,
              color: "rgba(255,255,255,0.5)",
              maxWidth: "45ch",
              letterSpacing: "-0.01em",
              marginBottom: "var(--content-gap)",
            }}
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            We&apos;re building something different. If you have questions, feedback,
            or want to partner, reach out.
          </motion.p>

          <div className="flex flex-wrap gap-4">
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
              Try Scribario
            </a>
            <a
              href="mailto:hello@scribario.com"
              className="inline-flex items-center gap-3 font-body font-medium transition-all duration-200 hover:scale-[1.02]"
              style={{
                backgroundColor: "rgba(255,255,255,0.06)",
                color: "#fff",
                borderRadius: 52,
                padding: "18px 36px",
                fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
                letterSpacing: "-0.01em",
                minHeight: 48,
                border: "1px solid rgba(255,255,255,0.1)",
              }}
            >
              Contact us
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
