"use client";

import type { Sender } from "@/types/conversation";

interface Props {
  content: string;
  sender: Sender;
  isFirst?: boolean;
}

export function MessageBubble({ content, sender, isFirst = true }: Props) {
  const isUser = sender === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[80%] px-4 py-2.5 text-sm leading-relaxed
          ${isUser
            ? "bg-[#2AABEE] text-white"
            : "bg-[#1E1E1E] text-[#f5f5f5]"
          }
          ${isFirst
            ? isUser
              ? "rounded-[18px] rounded-br-[4px]"
              : "rounded-[18px] rounded-bl-[4px]"
            : "rounded-[18px]"
          }
        `}
      >
        {content}
      </div>
    </div>
  );
}
