"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { AnimatePresence, motion } from "framer-motion";

const NAV_LINKS = [
  { href: "/features", label: "Features" },
  { href: "/how-it-works", label: "How It Works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/blog", label: "Blog" },
] as const;

export function Navbar() {
  const [onDark, setOnDark] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = useCallback(() => setMenuOpen(false), []);

  /* Lock body scroll when menu is open */
  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  /* Close on Escape */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeMenu();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [closeMenu]);

  useEffect(() => {
    let darkSections: Element[] = [];
    let prevDark = false;
    let prevScrolled = false;

    const check = () => {
      let isDark = false;
      for (const el of darkSections) {
        const rect = el.getBoundingClientRect();
        if (rect.top < 50 && rect.bottom > 50) { isDark = true; break; }
      }
      if (isDark !== prevDark) {
        prevDark = isDark;
        setOnDark(isDark);
      }
      const isScrolled = window.scrollY > 80;
      if (isScrolled !== prevScrolled) {
        prevScrolled = isScrolled;
        setScrolled(isScrolled);
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
      className="fixed top-0 left-0 w-full transition-all duration-300"
      style={{
        zIndex: 9999,
        backgroundColor: scrolled
          ? (onDark ? "rgba(10,10,15,0.85)" : "rgba(255,255,255,0.85)")
          : "transparent",
        backdropFilter: scrolled ? "blur(20px) saturate(180%)" : "none",
        WebkitBackdropFilter: scrolled ? "blur(20px) saturate(180%)" : "none",
        borderBottom: scrolled
          ? (onDark ? "1px solid rgba(255,255,255,0.08)" : "1px solid rgba(0,0,0,0.06)")
          : "1px solid transparent",
      }}
    >
      <div
        className="flex items-center justify-between px-[40px] max-[750px]:px-[6vw]"
        style={{ height: scrolled ? 64 : 80, transition: "height 0.3s ease" }}
      >
      {/* Logo */}
      <Link
        href="/"
        className="flex items-center gap-2 transition-colors duration-200"
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

      {/* Desktop nav links — hidden below 750px */}
      <div
        className="hidden min-[750px]:flex items-center"
        style={{ gap: "clamp(1.25rem, 2.5vw, 2.5rem)" }}
      >
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="transition-colors duration-200 hover:opacity-70"
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
          className="transition-colors duration-200 hover:opacity-70"
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

      {/* Hamburger button — visible below 750px */}
      <button
        aria-label={menuOpen ? "Close menu" : "Open menu"}
        aria-expanded={menuOpen}
        className="min-[750px]:hidden flex items-center justify-center"
        style={{ width: 44, height: 44 }}
        onClick={() => setMenuOpen((v) => !v)}
      >
        <div className="relative w-5 h-[14px]">
          <span
            className="absolute left-0 w-full h-[2px] rounded-full transition-all duration-300"
            style={{
              backgroundColor: onDark || menuOpen ? "#fff" : "#000",
              top: menuOpen ? 6 : 0,
              transform: menuOpen ? "rotate(45deg)" : "rotate(0deg)",
            }}
          />
          <span
            className="absolute left-0 top-[6px] w-full h-[2px] rounded-full transition-all duration-300"
            style={{
              backgroundColor: onDark || menuOpen ? "#fff" : "#000",
              opacity: menuOpen ? 0 : 1,
            }}
          />
          <span
            className="absolute left-0 w-full h-[2px] rounded-full transition-all duration-300"
            style={{
              backgroundColor: onDark || menuOpen ? "#fff" : "#000",
              top: menuOpen ? 6 : 12,
              transform: menuOpen ? "rotate(-45deg)" : "rotate(0deg)",
            }}
          />
        </div>
      </button>
      </div>

      {/* Mobile overlay menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="min-[750px]:hidden fixed inset-0"
            style={{
              top: 0,
              zIndex: 9998,
              backgroundColor: "rgba(10,10,15,0.97)",
              backdropFilter: "blur(24px)",
              WebkitBackdropFilter: "blur(24px)",
            }}
          >
            <nav
              className="flex flex-col items-center justify-center gap-6"
              style={{ height: "100dvh", paddingBottom: "env(safe-area-inset-bottom)" }}
            >
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.06 * i, duration: 0.25 }}
                >
                  <Link
                    href={link.href}
                    onClick={closeMenu}
                    className="block text-center transition-opacity hover:opacity-70"
                    style={{
                      color: "rgba(255,255,255,0.85)",
                      fontSize: "1.5rem",
                      fontWeight: 500,
                      letterSpacing: "-0.02em",
                      minHeight: 48,
                      lineHeight: "48px",
                    }}
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.06 * NAV_LINKS.length, duration: 0.25 }}
              >
                <a
                  href="https://t.me/ScribarioBot"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={closeMenu}
                  className="inline-block transition-opacity hover:opacity-90"
                  style={{
                    marginTop: 8,
                    padding: "14px 36px",
                    borderRadius: 999,
                    backgroundColor: "#FF6B4A",
                    color: "#fff",
                    fontSize: "1.125rem",
                    fontWeight: 600,
                    letterSpacing: "-0.01em",
                    textAlign: "center",
                  }}
                >
                  Try it free →
                </a>
              </motion.div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
