"use client";

import Link from "next/link";
import Image from "next/image";
import { EmailCapture } from "@/components/ui/EmailCapture";

const linkGroups = [
  {
    title: "Product",
    links: [
      { href: "/features", label: "Features" },
      { href: "/how-it-works", label: "How It Works" },
      { href: "/pricing", label: "Pricing" },
      { href: "/about", label: "About" },
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

export function Footer() {
  return (
    <footer
      data-dark
      style={{ backgroundColor: "var(--bg-dark)" }}
    >
      <div className="px-6 md:px-16" style={{ paddingTop: "var(--section-gap)", paddingBottom: "clamp(3rem, 6vw, 6rem)" }}>
        {/* Top: Brand + Newsletter */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-12 mb-16 md:mb-20">
          <div className="flex flex-col gap-4 max-w-xs">
            <div className="flex items-center gap-3">
              <Image
                src="/images/scribario-logo-final.webp"
                alt="Scribario"
                width={40}
                height={40}
                className="w-10 h-10 rounded-full"
              />
              <span
                className="font-display font-bold text-xl"
                style={{ color: "#fff" }}
              >
                Scribario
              </span>
            </div>
            <p
              style={{
                color: "rgba(255,255,255,0.45)",
                fontSize: "0.9rem",
                lineHeight: 1.6,
                letterSpacing: "-0.01em",
              }}
            >
              AI social media automation via Telegram. Text what you want, get three options, publish everywhere.
            </p>
          </div>

          {/* Newsletter */}
          <div className="max-w-md">
            <EmailCapture
              headline="Get social media tips and product updates."
              buttonText="Subscribe"
              source="footer"
              variant="dark"
            />
          </div>
        </div>

        {/* Link columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          {linkGroups.map((group) => (
            <div key={group.title} className="flex flex-col gap-3">
              <span
                className="font-mono uppercase"
                style={{
                  fontSize: "0.65rem",
                  letterSpacing: "0.1em",
                  color: "rgba(255,255,255,0.25)",
                }}
              >
                {group.title}
              </span>
              {group.links.map((link) => (
                <FooterLink
                  key={link.label}
                  href={link.href}
                  external={"external" in link && link.external}
                >
                  {link.label}
                </FooterLink>
              ))}
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          className="mt-16 pt-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
        >
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.8rem" }}>
            &copy; {new Date().getFullYear()} Scribario. All rights reserved.
          </p>
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.8rem" }}>
            Made with Telegram + AI
          </p>
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
  const style = {
    color: "rgba(255,255,255,0.45)",
    fontSize: "0.85rem",
    minHeight: 44,
    display: "flex" as const,
    alignItems: "center" as const,
    letterSpacing: "-0.01em",
  };

  if (external) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="transition-colors duration-150 hover:text-white"
        style={style}
      >
        {children}
      </a>
    );
  }
  return (
    <Link
      href={href}
      className="transition-colors duration-150 hover:text-white"
      style={style}
    >
      {children}
    </Link>
  );
}
