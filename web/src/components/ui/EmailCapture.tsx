"use client";

import { useState, useRef } from "react";

interface EmailCaptureProps {
  headline: string;
  buttonText?: string;
  source?: string;
  variant?: "light" | "dark";
}

export function EmailCapture({
  headline,
  buttonText = "Send it",
  source = "homepage",
  variant = "light",
}: EmailCaptureProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const isDark = variant === "dark";
  const inputBg = isDark ? "rgba(255,255,255,0.08)" : "#F5F5F7";
  const inputText = isDark ? "#fff" : "#000";
  const placeholderClass = isDark ? "placeholder:text-white/30" : "placeholder:text-black/30";
  const headlineColor = isDark ? "rgba(255,255,255,0.6)" : "var(--text-secondary)";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setStatus("error");
      setErrorMsg("Enter a valid email");
      inputRef.current?.focus();
      return;
    }

    setStatus("submitting");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });
      if (!res.ok) throw new Error("Failed");
      setStatus("success");
    } catch {
      setStatus("error");
      setErrorMsg("Something went wrong. Try again.");
    }
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-center gap-2">
        <p
          className="font-body"
          style={{
            fontSize: "clamp(1rem, 1.2vw, 1.2rem)",
            color: isDark ? "rgba(255,255,255,0.7)" : "var(--text-secondary)",
            letterSpacing: "-0.01em",
          }}
        >
          Check your inbox.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full" style={{ maxWidth: 520 }}>
      <p
        className="font-body text-center"
        style={{
          fontSize: "clamp(0.9rem, 1.1vw, 1.1rem)",
          color: headlineColor,
          letterSpacing: "-0.01em",
        }}
      >
        {headline}
      </p>
      <form
        onSubmit={handleSubmit}
        className="flex w-full gap-0 rounded-full overflow-hidden"
        style={{
          backgroundColor: inputBg,
          border: status === "error" ? "1px solid #E5553A" : "1px solid transparent",
        }}
      >
        <input
          ref={inputRef}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (status === "error") setStatus("idle");
          }}
          disabled={status === "submitting"}
          className={`flex-1 bg-transparent border-none outline-none font-body ${placeholderClass}`}
          style={{
            padding: "14px 20px",
            fontSize: "0.95rem",
            color: inputText,
            letterSpacing: "-0.01em",
            minHeight: 48,
          }}
        />
        <button
          type="submit"
          disabled={status === "submitting"}
          className="shrink-0 font-body font-medium transition-transform duration-150 hover:scale-[1.02] disabled:opacity-60"
          style={{
            backgroundColor: "var(--accent)",
            color: "#fff",
            padding: "14px 24px",
            fontSize: "0.9rem",
            letterSpacing: "-0.01em",
            border: "none",
            cursor: status === "submitting" ? "wait" : "pointer",
            minHeight: 48,
          }}
        >
          {status === "submitting" ? "..." : buttonText}
        </button>
      </form>
      {status === "error" && errorMsg && (
        <p style={{ color: "#E5553A", fontSize: "0.8rem" }}>{errorMsg}</p>
      )}
    </div>
  );
}
