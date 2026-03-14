"use client";

import { useRef, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { ConversationStep } from "@/types/conversation";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ImagePreview } from "./ImagePreview";
import { InlineButton } from "./InlineButton";
import { StatusMessage } from "./StatusMessage";

interface Props {
  visibleSteps: ConversationStep[];
}

export function TelegramChat({ visibleSteps }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const tappedLabels = useMemo(
    () =>
      new Set(
        visibleSteps
          .filter((s) => s.type === "tap")
          .map(
            (s) => (s as { type: "tap"; buttonLabel: string }).buttonLabel
          )
      ),
    [visibleSteps]
  );

  // Assign stable keys based on original insertion order
  const stepsWithKeys = useMemo(() => {
    let keyCounter = 0;
    return visibleSteps
      .filter((s) => s.type !== "tap")
      .map((step) => ({
        step,
        key: `${step.type}-${keyCounter++}-${"content" in step ? (step as { content: string }).content?.slice(0, 20) : step.type}`,
      }));
  }, [visibleSteps]);

  useEffect(() => {
    if (scrollRef.current) {
      const el = scrollRef.current;
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [visibleSteps]);

  return (
    <div className="flex flex-col h-full bg-[#1B1B1B] rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-[#1E1E1E] border-b border-white/5">
        <div className="w-9 h-9 rounded-full bg-[#FF6B4A] flex items-center justify-center text-[#050505] font-bold text-sm font-display">
          S
        </div>
        <div className="flex-1">
          <div className="text-sm font-medium text-[#f5f5f5]">Scribario</div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#FF6B4A] animate-pulse" />
            <span className="text-xs text-[#737373]">online</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-3 py-4 space-y-2.5"
        style={{ scrollbarWidth: "none" }}
      >
        <AnimatePresence mode="popLayout">
          {stepsWithKeys.map(({ step, key }) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
            >
              {step.type === "typing" && (
                <div className="flex items-end gap-2">
                  <BotAvatar />
                  <TypingIndicator />
                </div>
              )}

              {step.type === "text" && (
                <div
                  className={`flex ${step.sender === "user" ? "justify-end" : "items-end gap-2"}`}
                >
                  {step.sender === "bot" && <BotAvatar />}
                  <MessageBubble
                    content={step.content}
                    sender={step.sender}
                  />
                </div>
              )}

              {step.type === "images" && (
                <div className="flex items-end gap-2">
                  <div className="w-6 h-6 shrink-0" />
                  <ImagePreview images={step.images} />
                </div>
              )}

              {step.type === "buttons" && (
                <div className="flex items-end gap-2">
                  <div className="w-6 h-6 shrink-0" />
                  <div className="flex flex-col gap-1 w-full max-w-[80%]">
                    {step.rows.map((row, ri) => (
                      <div key={ri} className="flex gap-1">
                        {row.map((btn) => (
                          <InlineButton
                            key={btn.label}
                            label={btn.label}
                            variant={btn.variant}
                            tapped={tappedLabels.has(btn.label)}
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {step.type === "status" && (
                <div className="flex items-end gap-2">
                  <BotAvatar />
                  <StatusMessage
                    content={step.content}
                    platforms={step.platforms}
                  />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

function BotAvatar() {
  return (
    <div className="w-6 h-6 rounded-full bg-[#FF6B4A] flex items-center justify-center text-[8px] text-[#050505] font-bold shrink-0">
      S
    </div>
  );
}
