"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const features = [
  {
    label: "Content Creation",
    title: "AI Captions",
    description: "Five caption formulas — Hook-Story-Offer, PAS, Punchy, Story-Lesson, List-Value-Drop. Every post gets three unique options matched to your brand voice. Pick the one that hits.",
    accent: "var(--accent)",
    imageSrc: "/images/feat-captions.webp",
    imageAlt: "Phone screen showing three AI-generated social media caption options in a café — Scribario creates multiple captions for every post",
  },
  {
    label: "Visual AI",
    title: "AI Images & Video",
    description: "Photorealistic, cinematic, watercolor, cartoon — pick a style or let your brand default decide. Upload reference photos for consistency. Short-form video clips (5-10 seconds) available as an add-on.",
    accent: "var(--accent-secondary)",
    imageSrc: "/images/feat-images.webp",
    imageAlt: "Four versions of the same coffee shop in different AI art styles — photorealistic, cinematic, watercolor, and cartoon — showing Scribario's style system",
  },
  {
    label: "Publishing",
    title: "Publish to Facebook",
    description: "Facebook is fully connected. More platforms — Instagram, LinkedIn, X, TikTok, and others — are coming soon. Just hit approve and it's live.",
    accent: "var(--accent)",
    imageSrc: "/images/feat-platforms.webp",
    imageAlt: "Nine 3D social media platform icons arranged in a circle on a white desk — Facebook, Instagram, LinkedIn, TikTok, YouTube, and more — all connected through one tap",
  },
  {
    label: "Intelligence",
    title: "Brand Voice That Learns",
    description: "Every post you approve teaches Scribario your style. The more you use it, the more it sounds like you — not like every other AI tool. Your voice, amplified.",
    accent: "var(--accent-secondary)",
    imageSrc: "/images/feat-brand-voice.webp",
    imageAlt: "Handwritten brand tone of voice guidelines in a notebook next to a phone showing a matching social media post — Scribario learns your writing style",
  },
  {
    label: "Editing",
    title: "Refine in Natural Language",
    description: "Don't like a caption? Tap edit, say \"make it shorter\" or \"add a question hook.\" AI revises while keeping your brand voice. Regenerate just one image without losing the rest.",
    accent: "var(--accent)",
    imageSrc: "/images/feat-editing.webp",
    imageAlt: "Phone chat showing natural language editing — user says make it shorter, AI revises the caption instantly while keeping brand voice",
  },
  {
    label: "Workflow",
    title: "Schedule With Words",
    description: "\"Post this Friday at 9am.\" That's it. Natural language scheduling, post history at /history, and a workflow that fits how you actually think — not how software wants you to think.",
    accent: "var(--accent-secondary)",
    imageSrc: "/images/feat-scheduling.webp",
    imageAlt: "Minimal wall clock showing 9 AM with a phone on a shelf displaying a scheduling message — Scribario natural language scheduling",
  },
];

export function FeatureShowcase() {
  return (
    <section
      id="features"
      aria-labelledby="features-heading"
      style={{
        paddingTop: "var(--section-gap)",
        paddingBottom: "var(--section-gap)",
        backgroundColor: "var(--bg-alt)",
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
          What you get
        </motion.p>

        {/* Section heading */}
        <motion.h2
          id="features-heading"
          className="font-display font-bold"
          style={{
            fontSize: "clamp(2.5rem, 5vw, 5rem)",
            lineHeight: 1.04,
            letterSpacing: "-0.03em",
            color: "var(--text)",
            maxWidth: "16ch",
          }}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          More than you&apos;d expect from a text message.
        </motion.h2>

        {/* Feature blocks — alternating image + text layout */}
        <div className="flex flex-col" style={{ marginTop: "var(--content-gap)", gap: "var(--content-gap)" }}>
          {features.map((feature, i) => {
            const isEven = i % 2 === 0;
            return (
              <motion.div
                key={feature.title}
                className={`flex flex-col ${isEven ? "md:flex-row" : "md:flex-row-reverse"} gap-8 md:gap-12 items-start md:items-center`}
                style={{
                  paddingBottom: i < features.length - 1 ? "var(--content-gap)" : 0,
                  borderBottom: i < features.length - 1 ? "1px solid rgba(0,0,0,0.06)" : "none",
                }}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                {/* Image — floating with hover lift */}
                <motion.div
                  className="w-full md:w-5/12 shrink-0"
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
                      src={feature.imageSrc}
                      alt={feature.imageAlt}
                      fill
                      className="object-cover transition-transform duration-500 hover:scale-105"
                      sizes="(max-width: 768px) 100vw, 42vw"
                      loading="lazy"
                    />
                  </div>
                </motion.div>

                {/* Text content */}
                <div className="flex-1">
                  <p
                    className="font-mono uppercase"
                    style={{
                      fontSize: "0.7rem",
                      letterSpacing: "0.1em",
                      color: feature.accent,
                      marginBottom: "0.75rem",
                    }}
                  >
                    {feature.label}
                  </p>
                  <h3
                    className="font-display font-bold"
                    style={{
                      fontSize: "clamp(1.75rem, 3vw, 3rem)",
                      letterSpacing: "-0.02em",
                      color: "var(--text)",
                      lineHeight: 1.1,
                    }}
                  >
                    {feature.title}
                  </h3>
                  <p
                    className="font-body mt-4"
                    style={{
                      fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
                      lineHeight: 1.7,
                      color: "var(--text-secondary)",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
