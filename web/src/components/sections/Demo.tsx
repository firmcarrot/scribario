"use client";

import { motion } from "framer-motion";
import { CardStack, CardStackItem } from "@/components/ui/CardStack";

interface BusinessCard extends CardStackItem {
  tag: string;
}

const businesses: BusinessCard[] = [
  {
    id: 1,
    title: "Restaurants",
    description: "Daily specials, events, seasonal menus — posted in seconds",
    tag: "Food & Dining",
    imageSrc: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
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
  },
  {
    id: 4,
    title: "Salons",
    description: "Before/after transformations, openings, promotions",
    tag: "Beauty & Wellness",
    imageSrc: "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80",
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
  },
];

export function Demo() {
  return (
    <section
      id="demo"
      data-dark
      aria-labelledby="demo-heading"
      style={{
        backgroundColor: "var(--bg-dark)",
        marginTop: "clamp(6rem, 17.36vw, 17.36rem)",
        contain: "layout paint",
      }}
    >
      {/* Massive heading */}
      <motion.h2
        id="demo-heading"
        className="font-display font-bold px-6 md:px-16"
        aria-label="Works for any business"
        style={{
          fontSize: "clamp(3rem, 15vw, 15rem)",
          lineHeight: 1,
          letterSpacing: "-0.0575em",
          paddingTop: "clamp(4rem, 11.11vw, 11.11rem)",
          backgroundImage: "linear-gradient(93deg, rgb(255, 107, 74) -1%, rgba(0, 136, 204, 0.8) 34%, rgba(255,255,255,0.7) 85%)",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6 }}
      >
        <span className="block">Works for</span>
        <span className="block">any business</span>
      </motion.h2>

      {/* Subheading */}
      <motion.p
        className="px-6 md:px-16"
        style={{
          fontSize: "clamp(1.25rem, 2.7vw, 2.7rem)",
          lineHeight: 1.18,
          letterSpacing: "-0.0475em",
          color: "rgba(255,255,255,0.7)",
          maxWidth: "42ch",
          paddingTop: "clamp(2rem, 4vw, 4rem)",
        }}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        Restaurant specials, retail launches, service promos — just describe it.
      </motion.p>

      {/* Card Stack */}
      <div
        className="px-6 md:px-16"
        style={{
          paddingTop: "clamp(3rem, 6vw, 6rem)",
          paddingBottom: "clamp(6rem, 11.11vw, 11.11rem)",
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

      {/* Bottom link to CTA */}
      <motion.div
        className="text-center pb-16"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <a
          href="#final-cta"
          className="font-display font-bold transition-opacity duration-200 hover:opacity-70"
          style={{
            fontSize: "clamp(1rem, 1.4vw, 1.4rem)",
            color: "rgba(255,255,255,0.5)",
            letterSpacing: "-0.0475em",
          }}
          onClick={(e) => {
            e.preventDefault();
            document.getElementById("final-cta")?.scrollIntoView({ behavior: "smooth" });
          }}
        >
          See it work →
        </a>
      </motion.div>
    </section>
  );
}
