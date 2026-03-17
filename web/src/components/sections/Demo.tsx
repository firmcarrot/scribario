"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { CardStack, CardStackItem } from "@/components/ui/CardStack";

interface BusinessCard extends CardStackItem {
  tag: string;
  href?: string;
}

const businesses: BusinessCard[] = [
  {
    id: 1,
    title: "Restaurants",
    description: "Daily specials, events, seasonal menus — posted in seconds",
    tag: "Food & Dining",
    imageSrc: "/images/industries/restaurants.webp",
    href: "/for/restaurants",
  },
  {
    id: 2,
    title: "Agencies",
    description: "Client campaigns, case studies, thought leadership",
    tag: "Professional Services",
    imageSrc: "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
  },
  {
    id: 3,
    title: "Local Shops",
    description: "New arrivals, sales, store updates that drive foot traffic",
    tag: "Retail",
    imageSrc: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
    href: "/for/small-business",
  },
  {
    id: 4,
    title: "Salons",
    description: "Before/after transformations, openings, promotions",
    tag: "Beauty & Wellness",
    imageSrc: "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80",
    href: "/for/salons",
  },
  {
    id: 5,
    title: "Gyms",
    description: "Class schedules, member transformations, challenges",
    tag: "Fitness",
    imageSrc: "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80",
  },
  {
    id: 6,
    title: "Real Estate",
    description: "Listings, open houses, market updates that sell",
    tag: "Property",
    imageSrc: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&q=80",
    href: "/for/real-estate",
  },
];

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
            backgroundImage: "radial-gradient(ellipse 70% 60% at 60% 50%, rgba(0, 136, 204, 0.04) 0%, transparent 100%)",
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
        Industries
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
        Works for{" "}
        <span
          style={{
            backgroundImage: "linear-gradient(135deg, rgb(255, 107, 74), rgb(255, 160, 120))",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          any business.
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
        Restaurant specials, retail launches, service promos — just describe it.
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
          items={businesses}
          initialIndex={0}
          autoAdvance
          intervalMs={3000}
          pauseOnHover
          showDots
          cardWidth={520}
          cardHeight={340}
          overlap={0.48}
          spreadDeg={40}
          loop
        />
      </div>

      {/* Industry links for SEO */}
      <div className="px-6 md:px-16 flex flex-wrap gap-3">
        {businesses.filter(b => b.href).map((b) => (
          <Link
            key={b.title}
            href={b.href!}
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
            {b.title} →
          </Link>
        ))}
      </div>
    </section>
  );
}
