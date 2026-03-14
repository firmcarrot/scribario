"use client";

import { motion } from "framer-motion";

interface Props {
  label: string;
  variant: "approve" | "edit" | "reject" | "regen";
  tapped?: boolean;
}

const variantStyles: Record<string, string> = {
  approve: "text-[#2AABEE] border-[#2AABEE]/20",
  edit: "text-[#2AABEE] border-[#2AABEE]/20",
  reject: "text-red-400 border-red-400/20",
  regen: "text-[#2AABEE] border-[#2AABEE]/20",
};

export function InlineButton({ label, variant, tapped }: Props) {
  if (tapped) {
    return (
      <motion.div
        className="flex-1 text-center py-2 px-3 rounded-lg text-xs font-medium bg-[#FF6B4A] text-[#050505] border border-[#FF6B4A]"
        initial={{ scale: 0.95 }}
        animate={{ scale: [0.95, 1.05, 1.0] }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        {label}
      </motion.div>
    );
  }

  return (
    <div
      className={`flex-1 text-center py-2 px-3 rounded-lg text-xs font-medium border bg-[#1E1E1E] ${variantStyles[variant]}`}
    >
      {label}
    </div>
  );
}
