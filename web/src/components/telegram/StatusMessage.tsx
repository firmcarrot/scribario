"use client";

import { motion } from "framer-motion";

interface Props {
  content: string;
  platforms: string[];
}

const platformIcons: Record<string, string> = {
  Facebook: "📘",
  Instagram: "📷",
  LinkedIn: "💼",
  Threads: "🧵",
  X: "𝕏",
  TikTok: "🎵",
};

export function StatusMessage({ content, platforms }: Props) {
  return (
    <motion.div
      className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-[#1E1E1E] w-fit text-sm"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <span className="text-[#FF6B4A]">✅</span>
      <span className="text-[#f5f5f5]">{content}</span>
      <span className="flex items-center gap-1 ml-1">
        {platforms.map((p) => (
          <span key={p} title={p} className="text-xs">
            {platformIcons[p] || p}
          </span>
        ))}
      </span>
    </motion.div>
  );
}
