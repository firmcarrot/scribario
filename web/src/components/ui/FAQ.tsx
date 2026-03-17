"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQProps {
  items: FAQItem[];
  variant?: "light" | "dark";
}

export function FAQ({ items, variant = "light" }: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const isDark = variant === "dark";

  const textColor = isDark ? "#fff" : "var(--text)";
  const mutedColor = isDark ? "rgba(255,255,255,0.6)" : "var(--text-secondary)";
  const borderColor = isDark ? "rgba(255,255,255,0.08)" : "var(--faq-border)";

  return (
    <div className="flex flex-col">
      {items.map((item, i) => (
        <div
          key={item.question}
          style={{ borderBottom: `1px solid ${borderColor}` }}
        >
          <button
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            className="w-full flex items-center justify-between gap-4 text-left py-5 md:py-6 transition-opacity duration-150 hover:opacity-70"
            style={{ minHeight: 48 }}
            aria-expanded={openIndex === i}
          >
            <span
              className="font-body font-medium"
              style={{
                fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
                color: textColor,
                letterSpacing: "-0.01em",
              }}
            >
              {item.question}
            </span>
            <span
              className="shrink-0 transition-transform duration-200"
              style={{
                transform: openIndex === i ? "rotate(45deg)" : "rotate(0deg)",
                color: mutedColor,
                fontSize: "1.5rem",
                lineHeight: 1,
              }}
            >
              +
            </span>
          </button>
          <AnimatePresence>
            {openIndex === i && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <p
                  className="font-body pb-5 md:pb-6"
                  style={{
                    fontSize: "clamp(0.9rem, 1.05vw, 1.05rem)",
                    lineHeight: 1.7,
                    color: mutedColor,
                    letterSpacing: "-0.01em",
                    maxWidth: "65ch",
                  }}
                >
                  {item.answer}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}
