"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from "framer-motion";

/* ── Plan Data ── */
const plans = [
  {
    name: "Free",
    description: "Try it out. See the magic.",
    monthlyPrice: 0,
    annualPrice: 0,
    features: [
      "First 5 posts free — no card required",
      "1 connected platform",
      "AI-generated captions",
      "AI-generated images",
      "Basic brand voice",
    ],
    cta: "Start Free",
    popular: false,
  },
  {
    name: "Pro",
    description: "For creators who mean business.",
    monthlyPrice: 19,
    annualPrice: 15,
    features: [
      "Unlimited posts",
      "All platforms connected",
      "AI-generated captions",
      "AI-generated images",
      "Custom brand voice",
      "Video generation — $5 each",
      "Priority support",
    ],
    cta: "Get Pro",
    popular: true,
  },
  {
    name: "Business",
    description: "Scale across brands and locations.",
    monthlyPrice: 49,
    annualPrice: 39,
    features: [
      "Unlimited posts",
      "All platforms connected",
      "AI-generated captions",
      "AI-generated images",
      "Custom + multi-brand voice",
      "5 videos included, then $4 each",
      "Priority support",
      "Dedicated onboarding",
    ],
    cta: "Go Business",
    popular: false,
  },
];

/* ── FAQ Data ── */
const faqs = [
  {
    q: "What platforms do you support?",
    a: "Facebook, Instagram, X (Twitter), LinkedIn, and more coming soon. Connect them all from inside Telegram.",
  },
  {
    q: "How does video generation work?",
    a: "Text what you want — a product showcase, a promo reel, a behind-the-scenes clip. Our AI creates a 30-second video matched to your brand. Available on Pro ($5/video) and Business (5 included).",
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. No contracts, no cancellation fees. Your plan stays active until the end of your billing period.",
  },
  {
    q: "Do I need to install anything?",
    a: "No. Everything happens inside Telegram. Just open the Scribario bot and start texting. Works on any phone, tablet, or desktop.",
  },
  {
    q: "What happens after my 5 free posts?",
    a: "After your first 5 posts, you'll be prompted to choose a plan. Your connected platforms and brand voice settings stay saved — just pick a plan to keep posting.",
  },
  {
    q: "How is this different from Canva or Buffer?",
    a: "Those tools still require you to design and schedule. Scribario does both — you text a message, we create the post and publish it. No editors, no calendars, no learning curve.",
  },
];

/* ── Check Icon ── */
function CheckIcon() {
  return (
    <svg
      aria-hidden="true"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="shrink-0"
      style={{ color: "var(--accent)" }}
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

/* ── Pricing Card with 3D tilt + glow ── */
function PricingCard({
  plan,
  price,
  index,
}: {
  plan: (typeof plans)[0];
  price: number;
  index: number;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const springConfig = { stiffness: 300, damping: 30 };
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [6, -6]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-6, 6]), springConfig);
  const glowX = useSpring(useTransform(mouseX, [-0.5, 0.5], [0, 100]), springConfig);
  const glowY = useSpring(useTransform(mouseY, [-0.5, 0.5], [0, 100]), springConfig);

  function handleMouse(e: React.MouseEvent) {
    const rect = cardRef.current?.getBoundingClientRect();
    if (!rect) return;
    mouseX.set((e.clientX - rect.left) / rect.width - 0.5);
    mouseY.set((e.clientY - rect.top) / rect.height - 0.5);
  }

  function handleMouseLeave() {
    mouseX.set(0);
    mouseY.set(0);
  }

  return (
    <motion.div
      ref={cardRef}
      className="relative flex flex-col w-full md:flex-1"
      style={{
        maxWidth: 380,
        perspective: "1200px",
        zIndex: plan.popular ? 10 : 1,
      }}
      initial={{ opacity: 0, y: 60, scale: 0.95 }}
      whileInView={{ opacity: 1, y: 0, scale: plan.popular ? 1.03 : 1 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{
        duration: 0.7,
        delay: 0.2 + index * 0.15,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
    >
      <motion.div
        className="relative flex flex-col h-full overflow-hidden"
        style={{
          rotateX,
          rotateY,
          transformStyle: "preserve-3d",
          borderRadius: 24,
          border: plan.popular
            ? "1px solid rgba(255, 107, 74, 0.4)"
            : "1px solid rgba(255,255,255,0.07)",
          background: plan.popular
            ? "linear-gradient(145deg, rgba(255, 107, 74, 0.08) 0%, rgba(255,255,255,0.04) 40%, rgba(0,136,204,0.04) 100%)"
            : "linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.015) 100%)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          boxShadow: plan.popular
            ? "0 30px 80px -20px rgba(255, 107, 74, 0.15), 0 0 40px -10px rgba(255, 107, 74, 0.05), inset 0 1px 0 rgba(255,255,255,0.06)"
            : "0 20px 50px -20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)",
          padding: "clamp(2rem, 3vw, 3rem)",
        }}
        onMouseMove={handleMouse}
        onMouseLeave={handleMouseLeave}
        whileHover={{
          borderColor: plan.popular
            ? "rgba(255, 107, 74, 0.6)"
            : "rgba(255,255,255,0.15)",
          boxShadow: plan.popular
            ? "0 35px 90px -20px rgba(255, 107, 74, 0.25), 0 0 50px -10px rgba(255, 107, 74, 0.1), inset 0 1px 0 rgba(255,255,255,0.08)"
            : "0 30px 70px -20px rgba(0,0,0,0.5), 0 0 30px -5px rgba(255, 107, 74, 0.05), inset 0 1px 0 rgba(255,255,255,0.06)",
        }}
        transition={{ duration: 0.3 }}
      >
        {/* Cursor-following glow */}
        <motion.div
          className="absolute pointer-events-none"
          style={{
            width: 250,
            height: 250,
            borderRadius: "50%",
            background: plan.popular
              ? "radial-gradient(circle, rgba(255, 107, 74, 0.12) 0%, transparent 70%)"
              : "radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%)",
            left: glowX,
            top: glowY,
            transform: "translate(-50%, -50%)",
            filter: "blur(20px)",
          }}
        />

        {/* Popular badge — with breathing room */}
        {plan.popular && (
          <div
            className="absolute font-mono rounded-full"
            style={{
              top: -1,
              left: "50%",
              transform: "translate(-50%, -50%)",
              backgroundColor: "var(--accent)",
              color: "#fff",
              fontSize: "0.65rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              padding: "6px 18px",
              whiteSpace: "nowrap",
              boxShadow: "0 4px 20px rgba(255, 107, 74, 0.3)",
            }}
          >
            Most Popular
          </div>
        )}

        {/* Content — pushed down for popular to make room for badge */}
        <div style={{ paddingTop: plan.popular ? 12 : 0 }}>
          {/* Plan name */}
          <h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(1.5rem, 2.2vw, 2.2rem)",
              letterSpacing: "-0.0475em",
              color: "#fff",
            }}
          >
            {plan.name}
          </h2>

          {/* Description */}
          <p
            className="font-body"
            style={{
              fontSize: "clamp(0.85rem, 1vw, 1rem)",
              color: "rgba(255,255,255,0.45)",
              marginTop: 6,
            }}
          >
            {plan.description}
          </p>

          {/* Price */}
          <div className="flex items-baseline gap-1.5" style={{ marginTop: "clamp(1.5rem, 2vw, 2rem)" }}>
            <span
              className="font-display font-bold"
              style={{
                fontSize: "clamp(3rem, 4.5vw, 4.5rem)",
                letterSpacing: "-0.04em",
                lineHeight: 1,
                color: plan.popular ? "var(--accent)" : "#fff",
              }}
            >
              ${price}
            </span>
            {price > 0 && (
              <span
                className="font-body"
                style={{
                  fontSize: "clamp(0.9rem, 1.1vw, 1.1rem)",
                  color: "rgba(255,255,255,0.35)",
                }}
              >
                /mo
              </span>
            )}
          </div>

          {/* Divider — gradient line */}
          <div
            style={{
              height: 1,
              marginTop: "clamp(1.5rem, 2vw, 2rem)",
              marginBottom: "clamp(1.5rem, 2vw, 2rem)",
              background: plan.popular
                ? "linear-gradient(90deg, transparent, rgba(255, 107, 74, 0.25) 30%, rgba(255, 107, 74, 0.25) 70%, transparent)"
                : "linear-gradient(90deg, transparent, rgba(255,255,255,0.08) 30%, rgba(255,255,255,0.08) 70%, transparent)",
            }}
          />

          {/* Features */}
          <ul className="flex flex-col gap-3.5 flex-1" style={{ marginBottom: "clamp(2rem, 2.5vw, 2.5rem)" }}>
            {plan.features.map((feature) => (
              <li key={feature} className="flex items-start gap-3">
                <CheckIcon />
                <span
                  className="font-body"
                  style={{
                    fontSize: "clamp(0.85rem, 0.95vw, 0.95rem)",
                    color: "rgba(255,255,255,0.7)",
                    lineHeight: 1.5,
                  }}
                >
                  {feature}
                </span>
              </li>
            ))}
          </ul>

          {/* CTA Button */}
          <motion.a
            href="https://t.me/ScribarioBot"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-center font-body font-medium relative overflow-hidden"
            style={{
              backgroundColor: plan.popular
                ? "var(--accent)"
                : "rgba(255,255,255,0.06)",
              color: "#fff",
              borderRadius: 14,
              padding: "16px 0",
              fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
              letterSpacing: "-0.0175em",
              minHeight: 44,
              border: plan.popular
                ? "1px solid rgba(255, 107, 74, 0.5)"
                : "1px solid rgba(255,255,255,0.08)",
            }}
            whileHover={{
              scale: 1.02,
              backgroundColor: plan.popular ? "#E5553A" : "rgba(255,255,255,0.1)",
            }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.2 }}
          >
            {plan.cta}
          </motion.a>
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ── FAQ Item — better contrast + spacing ── */
function FAQItem({ q, a, index }: { q: string; a: string; index: number }) {
  const [open, setOpen] = useState(false);

  return (
    <motion.div
      style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-left group"
        style={{
          minHeight: 44,
          padding: "clamp(1.25rem, 1.8vw, 1.8rem) 0",
        }}
        aria-expanded={open}
      >
        <span
          className="font-body font-medium pr-6"
          style={{
            fontSize: "clamp(1rem, 1.25vw, 1.25rem)",
            letterSpacing: "-0.0275em",
            color: "rgba(255,255,255,0.85)",
            lineHeight: 1.4,
          }}
        >
          {q}
        </span>
        <motion.span
          className="shrink-0 flex items-center justify-center"
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            border: "1px solid rgba(255,255,255,0.1)",
            color: open ? "var(--accent)" : "rgba(255,255,255,0.35)",
            fontSize: "1.1rem",
            transition: "color 0.2s, border-color 0.2s",
            borderColor: open ? "rgba(255, 107, 74, 0.3)" : "rgba(255,255,255,0.1)",
          }}
          animate={{ rotate: open ? 45 : 0 }}
          transition={{ duration: 0.25 }}
        >
          +
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
            style={{ overflow: "hidden" }}
          >
            <p
              className="font-body"
              style={{
                fontSize: "clamp(0.9rem, 1.1vw, 1.1rem)",
                lineHeight: 1.7,
                color: "rgba(255,255,255,0.55)",
                maxWidth: "60ch",
                paddingBottom: "clamp(1.25rem, 1.8vw, 1.8rem)",
              }}
            >
              {a}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Main Page ── */
export default function PricingPage() {
  const [annual, setAnnual] = useState(false);

  return (
    <main
      id="main-content"
      data-dark
      style={{
        backgroundColor: "var(--bg-dark)",
        minHeight: "100vh",
        overflow: "hidden",
      }}
    >
      {/* ── Ambient background effects ── */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 0 }} aria-hidden="true">
        {/* Main coral glow — top center */}
        <div
          className="absolute"
          style={{
            top: "5%",
            left: "25%",
            width: "50%",
            height: "50%",
            backgroundImage:
              "radial-gradient(ellipse 80% 60% at 50% 40%, rgba(255, 107, 74, 0.07) 0%, transparent 100%)",
          }}
        />
        {/* Blue accent glow — bottom right */}
        <div
          className="absolute"
          style={{
            bottom: "10%",
            right: "10%",
            width: "40%",
            height: "40%",
            backgroundImage:
              "radial-gradient(ellipse 70% 50% at 60% 50%, rgba(0, 136, 204, 0.04) 0%, transparent 100%)",
          }}
        />
        {/* Noise texture overlay */}
        <div
          className="absolute inset-0"
          style={{
            opacity: 0.03,
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
            backgroundRepeat: "repeat",
            backgroundSize: "256px 256px",
          }}
        />
      </div>

      {/* ── Content ── */}
      <div className="relative" style={{ zIndex: 1 }}>
        {/* ── Hero heading ── */}
        <div
          className="px-6 md:px-16 text-center"
          style={{ paddingTop: "clamp(10rem, 16vw, 16rem)" }}
        >
          <motion.p
            className="font-mono"
            style={{
              fontSize: "clamp(0.65rem, 0.85vw, 0.85rem)",
              letterSpacing: "0.25em",
              textTransform: "uppercase",
              color: "var(--accent)",
              marginBottom: "clamp(1.5rem, 2.5vw, 2.5rem)",
            }}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            Pricing
          </motion.p>

          <motion.h1
            className="font-display font-bold"
            style={{
              fontSize: "clamp(3rem, 9vw, 9rem)",
              lineHeight: 0.95,
              letterSpacing: "-0.0575em",
            }}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: 0.8,
              delay: 0.2,
              ease: [0.25, 0.46, 0.45, 0.94],
            }}
          >
            <span style={{ color: "#fff" }}>Choose your</span>
            <br />
            <span
              style={{
                backgroundImage:
                  "linear-gradient(135deg, rgb(255, 107, 74) 0%, rgb(255, 140, 105) 60%, rgba(0, 136, 204, 0.8) 100%)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              plan
            </span>
          </motion.h1>

          <motion.p
            className="font-body mx-auto"
            style={{
              fontSize: "clamp(1.05rem, 1.5vw, 1.5rem)",
              lineHeight: 1.6,
              color: "rgba(255,255,255,0.45)",
              maxWidth: "38ch",
              marginTop: "clamp(2rem, 3vw, 3rem)",
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            Start free. Upgrade when you&apos;re addicted.
          </motion.p>
        </div>

        {/* ── Billing toggle ── */}
        <motion.div
          className="flex items-center justify-center gap-5"
          style={{ paddingTop: "clamp(3rem, 5vw, 5rem)" }}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.55 }}
        >
          <span
            className="font-body"
            style={{
              fontSize: "clamp(0.85rem, 1vw, 1rem)",
              color: !annual ? "#fff" : "rgba(255,255,255,0.35)",
              transition: "color 0.3s",
              fontWeight: !annual ? 500 : 400,
            }}
          >
            Monthly
          </span>
          <button
            onClick={() => setAnnual(!annual)}
            className="relative rounded-full transition-colors duration-300"
            style={{
              width: 56,
              height: 30,
              backgroundColor: annual ? "var(--accent)" : "rgba(255,255,255,0.12)",
              border: annual ? "1px solid rgba(255, 107, 74, 0.5)" : "1px solid rgba(255,255,255,0.1)",
              minHeight: 44,
              minWidth: 56,
              display: "flex",
              alignItems: "center",
              padding: "0 4px",
            }}
            aria-label={`Switch to ${annual ? "monthly" : "annual"} billing`}
          >
            <motion.div
              className="rounded-full bg-white"
              style={{
                width: 22,
                height: 22,
                boxShadow: "0 2px 6px rgba(0,0,0,0.25)",
              }}
              animate={{ x: annual ? 24 : 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          </button>
          <span
            className="font-body flex items-center gap-2.5"
            style={{
              fontSize: "clamp(0.85rem, 1vw, 1rem)",
              color: annual ? "#fff" : "rgba(255,255,255,0.35)",
              transition: "color 0.3s",
              fontWeight: annual ? 500 : 400,
            }}
          >
            Annual
            <AnimatePresence>
              {annual && (
                <motion.span
                  className="font-mono rounded-full"
                  style={{
                    backgroundColor: "rgba(255, 107, 74, 0.12)",
                    color: "var(--accent)",
                    fontSize: "0.7rem",
                    letterSpacing: "0.06em",
                    padding: "4px 10px",
                    whiteSpace: "nowrap",
                  }}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.2 }}
                >
                  Save 20%
                </motion.span>
              )}
            </AnimatePresence>
          </span>
        </motion.div>

        {/* ── Cards ── */}
        <div
          className="flex flex-col md:flex-row gap-8 md:gap-6 justify-center items-center md:items-stretch px-6 md:px-16 mx-auto"
          style={{
            paddingTop: "clamp(4rem, 6vw, 6rem)",
            maxWidth: 1200,
          }}
        >
          {plans.map((plan, i) => {
            const price = annual ? plan.annualPrice : plan.monthlyPrice;
            return <PricingCard key={plan.name} plan={plan} price={price} index={i} />;
          })}
        </div>

        {/* ── Video add-on callout ── */}
        <motion.div
          className="text-center mx-auto px-6"
          style={{ paddingTop: "clamp(3rem, 5vw, 5rem)" }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p
            className="font-body inline-block"
            style={{
              fontSize: "clamp(0.9rem, 1.1vw, 1.1rem)",
              color: "rgba(255,255,255,0.4)",
              padding: "12px 28px",
              borderRadius: 50,
              border: "1px solid rgba(255,255,255,0.06)",
              background: "rgba(255,255,255,0.02)",
            }}
          >
            Need video? Pro and Business plans unlock{" "}
            <span style={{ color: "var(--accent)" }}>AI video generation</span> — from $5 per video.
          </p>
        </motion.div>

        {/* ── Separator ── */}
        <div
          className="mx-auto"
          style={{
            marginTop: "clamp(6rem, 10vw, 10rem)",
            maxWidth: 800,
            height: 1,
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 20%, rgba(255,255,255,0.06) 80%, transparent 100%)",
          }}
        />

        {/* ── FAQ ── */}
        <div
          className="px-6 md:px-16 mx-auto"
          style={{
            paddingTop: "clamp(6rem, 10vw, 10rem)",
            paddingBottom: "clamp(3rem, 5vw, 5rem)",
            maxWidth: 800,
          }}
        >
          <motion.p
            className="font-mono"
            style={{
              fontSize: "clamp(0.65rem, 0.85vw, 0.85rem)",
              letterSpacing: "0.25em",
              textTransform: "uppercase",
              color: "var(--accent)",
              marginBottom: "clamp(1rem, 1.5vw, 1.5rem)",
            }}
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
          >
            FAQ
          </motion.p>

          <motion.h2
            className="font-display font-bold"
            style={{
              fontSize: "clamp(2.5rem, 6vw, 6rem)",
              lineHeight: 0.95,
              letterSpacing: "-0.0575em",
              color: "#fff",
              marginBottom: "clamp(3rem, 5vw, 5rem)",
            }}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Questions
          </motion.h2>

          <div>
            {faqs.map((faq, i) => (
              <FAQItem key={faq.q} q={faq.q} a={faq.a} index={i} />
            ))}
          </div>
        </div>

        {/* ── Bottom CTA ── */}
        <div
          className="px-6 md:px-16 text-center"
          style={{
            paddingTop: "clamp(6rem, 10vw, 10rem)",
            paddingBottom: "clamp(8rem, 14vw, 14rem)",
          }}
        >
          <motion.h2
            className="font-display font-bold mx-auto"
            style={{
              fontSize: "clamp(2.5rem, 7vw, 7rem)",
              lineHeight: 1.05,
              letterSpacing: "-0.0575em",
              backgroundImage:
                "linear-gradient(135deg, rgb(255, 107, 74) 0%, rgb(255, 140, 105) 40%, rgba(255,255,255,0.6) 100%)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              maxWidth: "18ch",
              marginBottom: "clamp(3rem, 5vw, 5rem)",
            }}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
          >
            Ready to stop overthinking your content?
          </motion.h2>

          <motion.a
            href="https://t.me/ScribarioBot"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 font-body font-medium"
            style={{
              backgroundColor: "var(--accent)",
              color: "#fff",
              borderRadius: 52,
              padding: "22px 44px",
              fontSize: "clamp(1.05rem, 1.4vw, 1.4rem)",
              letterSpacing: "-0.0175em",
              minHeight: 44,
              boxShadow: "0 8px 30px rgba(255, 107, 74, 0.25)",
            }}
            whileHover={{ scale: 1.04, boxShadow: "0 12px 40px rgba(255, 107, 74, 0.35)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            <svg
              aria-hidden="true"
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
            </svg>
            Text the bot now
          </motion.a>

          <motion.p
            className="font-mono"
            style={{
              fontSize: "clamp(0.7rem, 0.85vw, 0.85rem)",
              letterSpacing: "0.05em",
              color: "rgba(255,255,255,0.25)",
              marginTop: "clamp(2rem, 3vw, 3rem)",
            }}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.35 }}
          >
            Free to try · No signup required · Works on any phone
          </motion.p>
        </div>
      </div>
    </main>
  );
}
