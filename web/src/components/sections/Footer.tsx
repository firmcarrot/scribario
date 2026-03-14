"use client";

import Link from "next/link";
import Image from "next/image";

export function Footer() {
  return (
    <footer
      data-dark
      style={{ backgroundColor: "var(--bg-dark)" }}
    >
      <div className="px-6 md:px-16 py-16 md:py-20">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-12">
          {/* Brand */}
          <div className="flex flex-col gap-4">
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
                color: "rgba(255,255,255,0.55)",
                fontSize: "0.9rem",
                maxWidth: 280,
                lineHeight: 1.6,
              }}
            >
              Your social media team in a text.
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-wrap gap-8 md:gap-20">
            <div className="flex flex-col gap-3">
              <span
                className="font-display font-bold text-sm uppercase tracking-wider"
                style={{ color: "rgba(255,255,255,0.3)" }}
              >
                Product
              </span>
              <FooterLink href="https://t.me/ScribarioBot" external>Try the Bot</FooterLink>
            </div>
            <div className="flex flex-col gap-3">
              <span
                className="font-display font-bold text-sm uppercase tracking-wider"
                style={{ color: "rgba(255,255,255,0.3)" }}
              >
                Legal
              </span>
              <FooterLink href="/terms">Terms of Service</FooterLink>
              <FooterLink href="/privacy">Privacy Policy</FooterLink>
            </div>
            <div className="flex flex-col gap-3">
              <span
                className="font-display font-bold text-sm uppercase tracking-wider"
                style={{ color: "rgba(255,255,255,0.3)" }}
              >
                Contact
              </span>
              <FooterLink href="mailto:privacy@scribario.com">privacy@scribario.com</FooterLink>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div
          className="mt-16 pt-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
        >
          <p style={{ color: "rgba(255,255,255,0.25)", fontSize: "0.8rem" }}>
            &copy; {new Date().getFullYear()} Scribario. All rights reserved.
          </p>
          <p style={{ color: "rgba(255,255,255,0.25)", fontSize: "0.8rem" }}>
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
    color: "rgba(255,255,255,0.55)",
    fontSize: "0.9rem",
    minHeight: 44,
    display: "flex",
    alignItems: "center" as const,
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
