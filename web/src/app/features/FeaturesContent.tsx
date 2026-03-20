"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { FAQ } from "@/components/ui/FAQ";

/* ── Feature Data — ALL 14 capabilities ── */

interface FeatureGroup {
  label: string;
  title: string;
  description: string;
  features: {
    name: string;
    detail: string;
    icon: string;
  }[];
}

const featureGroups: FeatureGroup[] = [
  {
    label: "Content Creation",
    title: "Three options. Every time.",
    description:
      "Text what you want. Scribario's two-layer AI creates three unique caption-and-image combinations in under 60 seconds. Not templates — original content matched to your brand.",
    features: [
      {
        name: "AI Captions",
        detail:
          "Five caption formulas — Hook-Story-Offer, PAS, Punchy One-Liner, Story-Lesson, and List/Value Drop — automatically selected to match your message. Each caption is unique, not a rephrase of the same idea.",
        icon: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
      },
      {
        name: "AI Images",
        detail:
          "Powered by Nano Banana 2. Four style modes — photorealistic, cinematic, watercolor, cartoon — with per-post override or brand-level defaults. Upload reference photos for visual consistency.",
        icon: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z",
      },
      {
        name: "Short-Form Video",
        detail:
          "Tap \"Make Video\" on any post to generate a 5-10 second clip. Start frame, end frame, smooth animation. Available as an add-on on all paid plans.",
        icon: "M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z",
      },
    ],
  },
  {
    label: "Control & Refinement",
    title: "You're the editor. AI is the intern.",
    description:
      "Don't like something? Say so in plain English. Scribario revises without losing your brand voice.",
    features: [
      {
        name: "Caption Editing",
        detail:
          "Tap Edit and describe what you want changed — \"make it shorter,\" \"add a question hook,\" \"more professional tone.\" The AI revises while keeping your brand voice intact.",
        icon: "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z",
      },
      {
        name: "Image Regeneration",
        detail:
          "Don't like one image but love the caption? Regenerate just that image without losing the text. Mix and match until every element is right.",
        icon: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
      },
      {
        name: "Style Selection",
        detail:
          "Set a default visual style for your brand (\"always cinematic\") or override per post (\"make this one watercolor\"). Four AI-generated art directions to choose from.",
        icon: "M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01",
      },
      {
        name: "Reference Photos",
        detail:
          "Upload photos of your products, team, or spaces. Label them — Me, My Partner, My Product, Other — and the AI uses them as visual references for consistent imagery. EXIF data stripped automatically.",
        icon: "M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z",
      },
    ],
  },
  {
    label: "Brand & Publishing",
    title: "Your brand, everywhere, automatically.",
    description:
      "Connect once. Scribario handles formatting, hashtags, and platform-specific requirements. Facebook is live — more channels coming soon.",
    features: [
      {
        name: "Brand Voice Learning",
        detail:
          "Scribario learns from every post you approve. The more you use it, the better it matches your tone, vocabulary, and style. Few-shot learning with up to 20 reference examples.",
        icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
      },
      {
        name: "Logo Watermarking",
        detail:
          "Upload your logo once. It's automatically composited into every video — no manual editing, no forgetting to add it. Professional output every time.",
        icon: "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z",
      },
      {
        name: "Facebook Publishing",
        detail:
          "Facebook is fully connected. More platforms — Instagram, LinkedIn, X, TikTok, and others — are coming soon. Each platform will get properly formatted content when it goes live.",
        icon: "M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9",
      },
      {
        name: "Platform Targeting",
        detail:
          "Natural language controls for where and when to post. Currently publishing to Facebook, with more platforms coming soon. You control everything from the chat — no dashboards.",
        icon: "M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z",
      },
    ],
  },
  {
    label: "Workflow",
    title: "No dashboard. No learning curve.",
    description:
      "Everything happens in the same Telegram conversation. Schedule posts, review history, manage your brand — all through text.",
    features: [
      {
        name: "Natural Language Scheduling",
        detail:
          "\"Post this Friday at 9am\" — Scribario parses dates and times automatically. No calendar UI, no time pickers, no timezone dropdowns. Just tell it when.",
        icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
      },
      {
        name: "Autopilot Mode",
        detail:
          "Set a posting schedule and Scribario auto-generates and publishes content on your behalf. Pause or resume anytime with /pause and /resume. Like having a social media manager that never sleeps.",
        icon: "M13 10V3L4 14h7v7l9-11h-7z",
      },
      {
        name: "Content Library",
        detail:
          "Type /library to browse your past content and reuse what worked. Type /history to see your last 10 posts — date, platforms, caption preview. Track everything without leaving the conversation.",
        icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
      },
    ],
  },
];

const faqItems = [
  {
    question: "Does Scribario work for any type of business?",
    answer:
      "Yes. Restaurants, salons, real estate agents, gyms, agencies, local shops — any business that needs social media content. The AI adapts its writing style and visual treatment to match your industry.",
  },
  {
    question: "What AI models power Scribario?",
    answer:
      "Claude AI for caption writing and conversation understanding. Nano Banana 2 for image generation. Veo 3.1 for video generation. ElevenLabs for voiceover. The multi-model pipeline means each component uses the best AI for that specific task.",
  },
  {
    question: "How does brand voice learning work?",
    answer:
      "Every time you approve a post, Scribario saves it as a reference example. When creating new content, the AI references your approved posts to match your tone, vocabulary, and style. Up to 20 examples are used for few-shot learning.",
  },
  {
    question: "Can I use my own photos in posts?",
    answer:
      "Yes. Upload reference photos and label them — Me, My Partner, My Product, Other. The AI uses these as visual references when generating images, so your content features your actual products, team, or locations.",
  },
  {
    question: "How much does video generation cost?",
    answer:
      "Short-form video clips (5-10 seconds) are available as an add-on on all paid plans at $5/video, or included with Growth and Pro plans. Each video is AI-generated from your description.",
  },
];

/* ── Feature Icon ── */
function FeatureIcon({ path, accent }: { path: string; accent?: boolean }) {
  return (
    <div
      className="shrink-0 flex items-center justify-center rounded-xl"
      style={{
        width: 48,
        height: 48,
        backgroundColor: accent ? "rgba(255, 107, 74, 0.1)" : "var(--bg-alt)",
        border: accent
          ? "1px solid rgba(255, 107, 74, 0.2)"
          : "1px solid rgba(0,0,0,0.06)",
      }}
    >
      <svg
        width="22"
        height="22"
        viewBox="0 0 24 24"
        fill="none"
        stroke={accent ? "var(--accent)" : "var(--text)"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d={path} />
      </svg>
    </div>
  );
}

/* ── Main Content ── */
export function FeaturesContent() {
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
          Features
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
          Everything your social media needs.{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Nothing you don&apos;t.
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
          14 capabilities. One Telegram conversation. No dashboard, no learning curve,
          no design degree required.
        </motion.p>
      </section>

      {/* Feature Groups */}
      {featureGroups.map((group, gi) => {
        const isDark = gi % 2 === 1;
        return (
          <section
            key={group.label}
            {...(isDark ? { "data-dark": true } : {})}
            style={{
              backgroundColor: isDark ? "var(--bg-dark)" : gi === 2 ? "var(--bg-alt)" : "#fff",
              paddingTop: "var(--section-gap)",
              paddingBottom: "var(--section-gap)",
            }}
          >
            <div className="px-6 md:px-16">
              {/* Group header */}
              <motion.p
                className="font-mono"
                style={{
                  fontSize: "0.75rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: isDark ? "rgba(255,255,255,0.4)" : "var(--text-secondary)",
                  marginBottom: "clamp(1.5rem, 2vw, 2rem)",
                }}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5 }}
              >
                {group.label}
              </motion.p>

              <motion.h2
                className="font-display font-bold"
                style={{
                  fontSize: "clamp(2.5rem, 5vw, 5rem)",
                  lineHeight: 1.04,
                  letterSpacing: "-0.03em",
                  color: isDark ? "#fff" : "var(--text)",
                }}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                {group.title}
              </motion.h2>

              <motion.p
                className="font-body"
                style={{
                  fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
                  lineHeight: 1.5,
                  color: isDark ? "rgba(255,255,255,0.5)" : "var(--text-secondary)",
                  maxWidth: "50ch",
                  marginTop: "var(--item-gap)",
                  letterSpacing: "-0.01em",
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.15 }}
              >
                {group.description}
              </motion.p>

              {/* Feature cards */}
              <div
                className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8"
                style={{ marginTop: "var(--content-gap)" }}
              >
                {group.features.map((feat, fi) => (
                  <motion.div
                    key={feat.name}
                    className="flex flex-col gap-4"
                    style={{
                      padding: "clamp(1.5rem, 2.5vw, 2.5rem)",
                      borderRadius: 20,
                      backgroundColor: isDark
                        ? "rgba(255,255,255,0.04)"
                        : "#fff",
                      border: isDark
                        ? "1px solid rgba(255,255,255,0.06)"
                        : "1px solid rgba(0,0,0,0.06)",
                    }}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.1 + fi * 0.08 }}
                  >
                    <FeatureIcon path={feat.icon} accent={isDark} />
                    <h3
                      className="font-display font-bold"
                      style={{
                        fontSize: "clamp(1.25rem, 1.8vw, 1.8rem)",
                        letterSpacing: "-0.02em",
                        color: isDark ? "#fff" : "var(--text)",
                      }}
                    >
                      {feat.name}
                    </h3>
                    <p
                      className="font-body"
                      style={{
                        fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
                        lineHeight: 1.7,
                        color: isDark ? "rgba(255,255,255,0.6)" : "var(--text-secondary)",
                        letterSpacing: "-0.01em",
                      }}
                    >
                      {feat.detail}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>
        );
      })}

      {/* CTA + FAQ */}
      <section
        data-dark
        style={{
          backgroundColor: "var(--bg-dark)",
          paddingTop: "var(--section-gap)",
          paddingBottom: "var(--section-gap)",
        }}
      >
        <div className="px-6 md:px-16">
          {/* CTA */}
          <motion.div
            className="flex flex-col items-start gap-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2
              className="font-display font-bold"
              style={{
                fontSize: "clamp(2.5rem, 5vw, 5rem)",
                lineHeight: 1.04,
                letterSpacing: "-0.03em",
                color: "#fff",
              }}
            >
              See it in{" "}
              <span
                style={{
                  backgroundImage: "linear-gradient(135deg, #FF6B4A, #FF8C69)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                action.
              </span>
            </h2>
            <p
              className="font-body"
              style={{
                fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
                lineHeight: 1.5,
                color: "rgba(255,255,255,0.5)",
                maxWidth: "45ch",
                letterSpacing: "-0.01em",
              }}
            >
              Open Telegram. Search @ScribarioBot. Text what you want to post.
              That&apos;s it.
            </p>
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
              Try it free on Telegram
            </a>
          </motion.div>

          {/* FAQ */}
          <div style={{ marginTop: "var(--section-gap)" }}>
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
        </div>
      </section>
    </>
  );
}
