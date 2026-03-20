"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { CardStack, CardStackItem } from "@/components/ui/CardStack";

interface ProductCard extends CardStackItem {
  caption: string;
  niche: string;
  accentColor: string;
  accentGlow: string;
  href?: string;
}

const showcasePosts: ProductCard[] = [
  {
    id: 1,
    title: "Restaurant",
    niche: "Food & Dining",
    imageSrc: "/images/posts/happy-hour.webp",
    caption:
      "The sun's setting, the cocktails are flowing, and our chef just dropped a new tapas menu. Grab your crew — happy hour hits different on a rooftop.",
    accentColor: "#1877F2",
    accentGlow: "rgba(24, 119, 242, 0.15)",
    href: "/for/restaurants",
  },
  {
    id: 2,
    title: "Real Estate",
    niche: "Property",
    imageSrc: "/images/posts/re-listing.webp",
    caption:
      "Just listed in Riverside Heights. 4 bed, 3 bath, floor-to-ceiling windows, and a backyard that hosts itself. Open house this Saturday 1–4 PM.",
    accentColor: "#E1306C",
    accentGlow: "rgba(225, 48, 108, 0.15)",
    href: "/for/real-estate",
  },
  {
    id: 3,
    title: "Salon",
    niche: "Beauty & Wellness",
    imageSrc: "/images/posts/salon-transform.webp",
    caption:
      "From box dye breakage to balayage perfection. 3 sessions, zero damage, 100% confidence. This is what a color correction journey looks like.",
    accentColor: "#000000",
    accentGlow: "rgba(255, 255, 255, 0.08)",
    href: "/for/salons",
  },
  {
    id: 4,
    title: "Retail",
    niche: "Local Shop",
    imageSrc: "/images/posts/sb-product.webp",
    caption:
      "New drop just hit the shelves. Handmade ceramic mugs from a local artist — each one unique. Only 12 made. First come, first served.",
    accentColor: "#0A66C2",
    accentGlow: "rgba(10, 102, 194, 0.15)",
    href: "/for/small-business",
  },
  {
    id: 5,
    title: "Fitness",
    niche: "Health & Wellness",
    imageSrc: "/images/posts/sb-tips.webp",
    caption:
      "Monday motivation: you don't need 2 hours in the gym. 30 focused minutes beats 90 distracted ones. Here are 3 compound moves that change everything.",
    accentColor: "#FF0050",
    accentGlow: "rgba(255, 0, 80, 0.15)",
  },
  {
    id: 6,
    title: "Professional",
    niche: "Agency & Services",
    imageSrc: "/images/posts/sb-thanks.webp",
    caption:
      "We just wrapped our biggest project of the quarter. Grateful for clients who trust the process and a team that delivers under pressure.",
    accentColor: "#FF0000",
    accentGlow: "rgba(255, 0, 0, 0.12)",
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
    <div className="relative h-full w-full overflow-hidden" style={{ background: "#111" }}>
      {/* Platform color accent — top strip */}
      <div
        style={{
          height: 3,
          background: item.accentColor,
          opacity: active ? 1 : 0.5,
          transition: "opacity 0.3s",
        }}
      />

      {/* Full image background */}
      {item.imageSrc && (
        <img
          src={item.imageSrc}
          alt={`AI-generated ${item.niche.toLowerCase()} social media post`}
          className="absolute inset-0 w-full h-full object-cover"
          draggable={false}
          loading="eager"
        />
      )}

      {/* Gradient overlay — bottom half darkens for text */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "linear-gradient(to bottom, transparent 30%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.85) 75%, rgba(0,0,0,0.95) 100%)",
        }}
      />

      {/* Caption content — pinned to bottom */}
      <div className="absolute inset-x-0 bottom-0 px-5 pb-4 pt-6">
        {/* Niche label with platform-colored dot */}
        <div className="flex items-center gap-2 mb-2">
          <span
            className="block rounded-full"
            style={{
              width: 6,
              height: 6,
              backgroundColor: item.accentColor,
              boxShadow: `0 0 8px ${item.accentGlow}`,
            }}
          />
          <span
            className="font-mono uppercase"
            style={{
              fontSize: "0.65rem",
              letterSpacing: "0.1em",
              color: "rgba(255,255,255,0.5)",
            }}
          >
            {item.niche}
          </span>
        </div>

        {/* AI-generated caption */}
        <p
          className="font-body leading-snug line-clamp-3"
          style={{
            fontSize: "0.85rem",
            color: "rgba(255,255,255,0.92)",
            letterSpacing: "-0.01em",
          }}
        >
          {item.caption}
        </p>

        {/* "AI-generated" badge */}
        <div className="flex items-center gap-1.5 mt-3">
          <span
            className="font-mono"
            style={{
              fontSize: "0.6rem",
              letterSpacing: "0.08em",
              color: "rgba(255,255,255,0.3)",
              textTransform: "uppercase",
            }}
          >
            Generated by Scribario AI
          </span>
        </div>
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
        Every caption and image below was generated by Scribario — not a
        copywriter, not a designer.
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
          cardWidth={500}
          cardHeight={380}
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

      {/* Industry links for SEO */}
      <div className="px-6 md:px-16 flex flex-wrap gap-3">
        {showcasePosts
          .filter((p) => p.href)
          .map((p) => (
            <Link
              key={p.title}
              href={p.href!}
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
              {p.title} →
            </Link>
          ))}
      </div>
    </section>
  );
}
