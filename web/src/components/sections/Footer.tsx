"use client";

import Link from "next/link";
import Image from "next/image";
import { EmailCapture } from "@/components/ui/EmailCapture";
import { Send, Instagram, Facebook } from "lucide-react";

const linkGroups = [
  {
    title: "Product",
    links: [
      { href: "/features", label: "Features" },
      { href: "/how-it-works", label: "How It Works" },
      { href: "/pricing", label: "Pricing" },
      { href: "/about", label: "About" },
      { href: "/blog", label: "Blog" },
      { href: "https://t.me/ScribarioBot", label: "Try the Bot", external: true },
    ],
  },
  {
    title: "Industries",
    links: [
      { href: "/for/restaurants", label: "Restaurants" },
      { href: "/for/real-estate", label: "Real Estate" },
      { href: "/for/salons", label: "Salons" },
      { href: "/for/small-business", label: "Small Business" },
    ],
  },
  {
    title: "Compare",
    links: [
      { href: "/compare/vs-buffer", label: "vs Buffer" },
      { href: "/compare/vs-hootsuite", label: "vs Hootsuite" },
      { href: "/compare/vs-canva", label: "vs Canva" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/terms", label: "Terms of Service" },
      { href: "/privacy", label: "Privacy Policy" },
      { href: "mailto:privacy@scribario.com", label: "Contact", external: true },
    ],
  },
];

const socials = [
  { Icon: Send, href: "https://t.me/ScribarioBot", label: "Telegram" },
  { Icon: Facebook, href: "https://facebook.com/scribario", label: "Facebook" },
  { Icon: Instagram, href: "https://instagram.com/scribario", label: "Instagram" },
];

export function Footer() {
  return (
    <footer
      data-dark
      className="relative overflow-hidden"
      style={{ backgroundColor: "var(--bg-dark)" }}
    >
      {/* Background Tech Pattern */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
          maskImage: "radial-gradient(circle at center, black, transparent 80%)",
          WebkitMaskImage: "radial-gradient(circle at center, black, transparent 80%)",
        }}
      />

      <div
        className="relative z-10 max-w-6xl mx-auto px-6 md:px-16"
        style={{
          paddingTop: "var(--section-gap)",
          paddingBottom: "clamp(2rem, 4vw, 4rem)",
        }}
      >
        <div className="grid grid-cols-2 md:grid-cols-12 gap-8 md:gap-8 mb-16">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-4 flex flex-col gap-6">
            <div className="flex items-center gap-3">
              <Image
                src="/images/scribario-logo-final.webp"
                alt="Scribario"
                width={32}
                height={32}
                className="w-8 h-8 rounded-full"
                style={{
                  boxShadow: "0 0 12px rgba(255,107,74,0.3)",
                }}
              />
              <span
                className="font-display font-bold text-xl tracking-tight"
                style={{ color: "#fff" }}
              >
                Scribario
              </span>
            </div>
            <p
              style={{
                color: "rgba(255,255,255,0.45)",
                fontSize: "0.9rem",
                lineHeight: 1.7,
                letterSpacing: "-0.01em",
                maxWidth: 320,
              }}
            >
              Next Generation Social Media Content Creation is Here.
              Replace Your Team with a Text.
            </p>

            {/* Newsletter */}
            <div className="mt-2">
              <EmailCapture
                headline="Get social media tips and product updates."
                buttonText="Subscribe"
                source="footer"
                variant="dark"
              />
            </div>
          </div>

          {/* Link Columns — 2-col on mobile, spread across remaining 8 cols on desktop */}
          {linkGroups.map((group) => (
            <div
              key={group.title}
              className="col-span-1 md:col-span-2 flex flex-col gap-4"
            >
              <span
                className="font-mono font-semibold uppercase"
                style={{
                  fontSize: "0.65rem",
                  letterSpacing: "0.12em",
                  color: "rgba(255,255,255,0.35)",
                }}
              >
                {group.title}
              </span>
              <ul className="flex flex-col gap-3">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <FooterLink
                      href={link.href}
                      external={"external" in link && link.external}
                    >
                      {link.label}
                    </FooterLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div
          className="flex flex-col md:flex-row items-center justify-between gap-6 pt-8"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
        >
          <p
            className="font-mono"
            style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.75rem" }}
          >
            &copy; {new Date().getFullYear()} DarkArc Technologies LLC
          </p>

          <div className="flex items-center gap-6">
            {/* Socials */}
            <div
              className="flex gap-4 pr-6 mr-2"
              style={{ borderRight: "1px solid rgba(255,255,255,0.1)" }}
            >
              {socials.map(({ Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="transition-colors duration-150"
                  style={{ color: "rgba(255,255,255,0.25)" }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.color = "#fff")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.color = "rgba(255,255,255,0.25)")
                  }
                >
                  <Icon size={18} />
                </a>
              ))}
            </div>

            {/* Status Indicator */}
            <div
              className="flex items-center gap-2 px-3 py-1 rounded-full"
              style={{
                backgroundColor: "rgba(34,197,94,0.05)",
                border: "1px solid rgba(34,197,94,0.1)",
              }}
            >
              <div
                className="rounded-full animate-pulse"
                style={{
                  width: 6,
                  height: 6,
                  backgroundColor: "rgb(34,197,94)",
                }}
              />
              <span
                className="font-mono font-medium uppercase"
                style={{
                  fontSize: "0.6rem",
                  letterSpacing: "0.08em",
                  color: "rgba(34,197,94,0.8)",
                }}
              >
                All Systems Normal
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterLink({
  href,
  children,
  external,
}: {
  href: string;
  children: React.ReactNode;
  external?: boolean;
}) {
  const className =
    "text-sm font-mono flex items-center gap-2 group w-fit transition-colors duration-150";

  const content = (
    <>
      <span
        className="rounded-full transition-all duration-200 group-hover:w-4"
        style={{
          width: 8,
          height: 8,
          backgroundColor: "rgba(255,255,255,0.1)",
          flexShrink: 0,
        }}
      />
      <span>{children}</span>
    </>
  );

  // Hover handler to swap colors (coral orange on hover)
  const handleEnter = (e: React.MouseEvent<HTMLElement>) => {
    e.currentTarget.style.color = "#FF6B4A";
    const dot = e.currentTarget.querySelector<HTMLSpanElement>("span:first-child");
    if (dot) dot.style.backgroundColor = "#FF6B4A";
  };
  const handleLeave = (e: React.MouseEvent<HTMLElement>) => {
    e.currentTarget.style.color = "rgba(255,255,255,0.45)";
    const dot = e.currentTarget.querySelector<HTMLSpanElement>("span:first-child");
    if (dot) dot.style.backgroundColor = "rgba(255,255,255,0.1)";
  };

  if (external) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className={className}
        style={{ color: "rgba(255,255,255,0.45)" }}
        onMouseEnter={handleEnter}
        onMouseLeave={handleLeave}
      >
        {content}
      </a>
    );
  }

  return (
    <Link
      href={href}
      className={className}
      style={{ color: "rgba(255,255,255,0.45)" }}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      {content}
    </Link>
  );
}
