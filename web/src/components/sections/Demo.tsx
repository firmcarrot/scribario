"use client";

import { motion } from "framer-motion";
import { CardStack, CardStackItem } from "@/components/ui/CardStack";

interface ProductCard extends CardStackItem {
  niche: string;
  accentColor: string;
  accentGlow: string;
}

const showcasePosts: ProductCard[] = [
  {
    id: 1,
    title: "No More Canva",
    niche: "Before & After",
    imageSrc: "/images/posts/fb-canva-vs-scribario.webp",
    accentColor: "#1877F2",
    accentGlow: "rgba(24, 119, 242, 0.15)",
  },
  {
    id: 2,
    title: "Content Creator",
    niche: "Workspace",
    imageSrc: "/images/posts/fb-cafe-workspace.webp",
    accentColor: "#0A66C2",
    accentGlow: "rgba(10, 102, 194, 0.15)",
  },
  {
    id: 3,
    title: "Salon Showcase",
    niche: "Beauty & Wellness",
    imageSrc: "/images/posts/fb-salon-collage.webp",
    accentColor: "#E1306C",
    accentGlow: "rgba(225, 48, 108, 0.15)",
  },
  {
    id: 4,
    title: "Social Manager",
    niche: "Professional",
    imageSrc: "/images/posts/fb-salon-portrait.webp",
    accentColor: "#FF6B4A",
    accentGlow: "rgba(255, 107, 74, 0.15)",
  },
  {
    id: 5,
    title: "Text & Post",
    niche: "How It Works",
    imageSrc: "/images/posts/fb-phone-text.webp",
    accentColor: "#0088CC",
    accentGlow: "rgba(0, 136, 204, 0.15)",
  },
];

function ProductShowcaseCard({
  item,
  active,
}: {
  item: ProductCard;
  active: boolean;
}) {
  return (
    <div
      className="relative h-full w-full overflow-hidden rounded-lg"
      style={{ background: "#1a1a2e" }}
    >
      {/* Platform color accent — top strip */}
      <div
        style={{
          height: 3,
          background: item.accentColor,
          opacity: active ? 1 : 0.5,
          transition: "opacity 0.3s",
        }}
      />

      {/* Full Facebook post screenshot */}
      {item.imageSrc && (
        <div className="flex items-center justify-center w-full h-full">
          <img
            src={item.imageSrc}
            alt={`Real Scribario post — ${item.niche.toLowerCase()}`}
            className="w-full h-full object-contain"
            draggable={false}
            loading="eager"
          />
        </div>
      )}

      {/* Subtle "Live on Facebook" badge — bottom */}
      <div
        className="absolute bottom-0 inset-x-0 flex items-center justify-center gap-1.5 py-2"
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, transparent 100%)",
        }}
      >
        <span
          className="font-mono"
          style={{
            fontSize: "0.6rem",
            letterSpacing: "0.08em",
            color: "rgba(255,255,255,0.5)",
            textTransform: "uppercase",
          }}
        >
          Real post — live on Facebook
        </span>
      </div>
    </div>
  );
}

export function Demo() {
  return (
    <section
      id="industries"
      data-dark
      aria-labelledby="demo-heading"
      className="relative overflow-hidden"
      style={{
        backgroundColor: "var(--bg-dark)",
        contain: "layout paint",
        paddingTop: "var(--section-gap)",
        paddingBottom: "var(--section-gap)",
      }}
    >
      {/* Ambient glow */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div
          className="absolute"
          style={{
            bottom: "10%",
            right: "15%",
            width: "50%",
            height: "50%",
            backgroundImage:
              "radial-gradient(ellipse 70% 60% at 60% 50%, rgba(0, 136, 204, 0.04) 0%, transparent 100%)",
          }}
        />
      </div>

      {/* Section label */}
      <motion.p
        className="font-mono px-6 md:px-16"
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
        Real output
      </motion.p>

      {/* Heading */}
      <motion.h2
        id="demo-heading"
        className="font-display font-bold px-6 md:px-16"
        style={{
          fontSize: "clamp(2.5rem, 5vw, 5rem)",
          lineHeight: 1.04,
          letterSpacing: "-0.03em",
          color: "#fff",
        }}
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        This is what{" "}
        <span
          style={{
            backgroundImage:
              "linear-gradient(135deg, rgb(255, 107, 74), rgb(255, 160, 120))",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          AI creates.
        </span>
      </motion.h2>

      {/* Subheading */}
      <motion.p
        className="px-6 md:px-16"
        style={{
          fontSize: "clamp(1.1rem, 1.5vw, 1.5rem)",
          lineHeight: 1.5,
          color: "rgba(255,255,255,0.5)",
          maxWidth: "50ch",
          marginTop: "var(--item-gap)",
          letterSpacing: "-0.01em",
        }}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.15 }}
      >
        Real posts. Real Facebook page. Every image and caption below was
        created and published by Scribario — no designer, no copywriter, no Canva.
      </motion.p>

      {/* Card Stack */}
      <div
        className="px-6 md:px-16"
        style={{
          paddingTop: "var(--content-gap)",
          paddingBottom: "var(--content-gap)",
        }}
      >
        <CardStack
          items={showcasePosts}
          initialIndex={0}
          autoAdvance
          intervalMs={4000}
          pauseOnHover
          showDots
          cardWidth={420}
          cardHeight={580}
          overlap={0.48}
          spreadDeg={40}
          loop
          renderCard={(item, { active }) => (
            <ProductShowcaseCard
              item={item as ProductCard}
              active={active}
            />
          )}
        />
      </div>

      {/* Real proof badge */}
      <div className="px-6 md:px-16 flex items-center gap-2">
        <span
          className="block rounded-full"
          style={{
            width: 6,
            height: 6,
            backgroundColor: "#22c55e",
            boxShadow: "0 0 8px rgba(34, 197, 94, 0.4)",
          }}
        />
        <span
          className="font-mono uppercase"
          style={{
            fontSize: "0.7rem",
            letterSpacing: "0.08em",
            color: "rgba(255,255,255,0.35)",
          }}
        >
          Every post above is real — generated and published by Scribario
        </span>
      </div>
    </section>
  );
}
