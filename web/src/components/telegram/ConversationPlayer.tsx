"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import type { ConversationStep } from "@/types/conversation";
import { useConversationPlayer } from "@/hooks/useConversationPlayer";
import { PhoneMockup } from "./PhoneMockup";
import { TelegramChat } from "./TelegramChat";

interface Props {
  steps: ConversationStep[];
  className?: string;
}

export function ConversationPlayer({ steps, className = "" }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { amount: 0.15 });
  const { visibleSteps } = useConversationPlayer(steps, isInView);

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      <PhoneMockup>
        <TelegramChat visibleSteps={visibleSteps} />
      </PhoneMockup>
    </motion.div>
  );
}
