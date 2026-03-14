import type { Metadata } from "next";
import { Navbar } from "@/components/ui/Navbar";
import { MotionProvider } from "@/components/ui/MotionProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Scribario — Your social media team in a text",
  description:
    "Text what you want. AI creates 3 unique caption + image options. One tap publishes everywhere. Social media on autopilot from Telegram.",
  metadataBase: new URL("https://scribario.com"),
  openGraph: {
    title: "Scribario — Your social media team in a text",
    description:
      "Text what you want. AI creates it. One tap publishes everywhere.",
    url: "https://scribario.com",
    siteName: "Scribario",
    images: [
      {
        url: "/images/demo/og.webp",
        width: 1200,
        height: 630,
        alt: "Scribario — Social media on autopilot",
      },
    ],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    site: "@scribario",
    title: "Scribario — Your social media team in a text",
    description:
      "Text what you want. AI creates it. One tap publishes everywhere.",
    images: ["/images/demo/og.webp"],
  },
  robots: { index: true, follow: true },
  alternates: { canonical: "https://scribario.com" },
  other: { "theme-color": "#ffffff", "color-scheme": "light" },
  icons: {
    apple: "/images/demo/favicon.webp",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="preload"
          href="/fonts/ClashDisplay-Bold.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="/fonts/CabinetGrotesk-Medium.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="/fonts/CabinetGrotesk-Regular.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              name: "Scribario",
              applicationCategory: "BusinessApplication",
              operatingSystem: "Web, Telegram",
              description:
                "AI-powered social media automation. Text what you want, AI creates it, one tap publishes everywhere.",
              url: "https://scribario.com",
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
                description: "Early access",
              },
              publisher: {
                "@type": "Organization",
                name: "Scribario",
                logo: {
                  "@type": "ImageObject",
                  url: "https://scribario.com/images/demo/favicon.webp",
                },
                sameAs: ["https://t.me/ScribarioBot"],
              },
            }),
          }}
        />
      </head>
      <body className="font-body antialiased">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg focus:text-black"
        >
          Skip to main content
        </a>
        <MotionProvider>
          <Navbar />
          {children}
        </MotionProvider>
      </body>
    </html>
  );
}
