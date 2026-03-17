"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";

export function Navbar() {
  const [onDark, setOnDark] = useState(false);

  useEffect(() => {
    let darkSections: Element[] = [];
    let prev = false;

    const check = () => {
      let isDark = false;
      for (const el of darkSections) {
        const rect = el.getBoundingClientRect();
        if (rect.top < 50 && rect.bottom > 50) { isDark = true; break; }
      }
      if (isDark !== prev) {
        prev = isDark;
        setOnDark(isDark);
      }
    };

    const cacheSections = () => {
      darkSections = Array.from(document.querySelectorAll("[data-dark]"));
      check();
    };

    cacheSections();

    // Watch for DOM changes (App Router page transitions swap content)
    const observer = new MutationObserver(() => { cacheSections(); });
    observer.observe(document.body, { childList: true, subtree: true });

    window.addEventListener("scroll", check, { passive: true });
    window.addEventListener("resize", cacheSections);
    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", check);
      window.removeEventListener("resize", cacheSections);
    };
  }, []);

  return (
    <nav
      aria-label="Main navigation"
      className="fixed top-0 left-0 w-full pointer-events-none"
      style={{ height: 0, zIndex: 4 }}
    >
      {/* Logo */}
      <Link
        href="/"
        className="pointer-events-auto absolute flex items-center gap-2 transition-colors duration-200 top-[38px] left-[40px] max-[750px]:top-[26px] max-[750px]:left-[6vw]"
        style={{ minHeight: 44 }}
      >
        <Image
          src="/images/scribario-logo-final.webp"
          alt="Scribario"
          width={36}
          height={36}
          className="w-9 h-9 max-[750px]:w-8 max-[750px]:h-8 rounded-full"
          priority
        />
        <span
          className="font-display font-bold text-lg transition-colors duration-200"
          style={{ color: onDark ? "#fff" : "#000" }}
        >
          Scribario
        </span>
      </Link>

      {/* Nav links — right side */}
      <div
        className="pointer-events-auto absolute flex items-center top-[38px] right-[40px] max-[750px]:top-[26px] max-[750px]:right-[6vw]"
        style={{ gap: "clamp(1.25rem, 2.5vw, 2.5rem)" }}
      >
        {[
          { href: "/features", label: "Features" },
          { href: "/how-it-works", label: "How It Works" },
          { href: "/pricing", label: "Pricing" },
        ].map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="transition-colors duration-200 hover:opacity-70 max-[750px]:text-sm max-[750px]:hidden"
            style={{
              color: onDark ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.6)",
              fontWeight: 500,
              letterSpacing: "-0.0175em",
              minHeight: 44,
              display: "flex",
              alignItems: "center",
            }}
          >
            {link.label}
          </Link>
        ))}
        <a
          href="https://t.me/ScribarioBot"
          target="_blank"
          rel="noopener noreferrer"
          className="transition-colors duration-200 hover:opacity-70 max-[750px]:text-sm"
          style={{
            color: onDark ? "#fff" : "#000",
            fontWeight: 500,
            letterSpacing: "-0.0175em",
            minHeight: 44,
            display: "flex",
            alignItems: "center",
          }}
        >
          Try it free →
        </a>
      </div>
    </nav>
  );
}
