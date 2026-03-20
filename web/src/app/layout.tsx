import type { Metadata } from "next";
import { Navbar } from "@/components/ui/Navbar";
import { MotionProvider } from "@/components/ui/MotionProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Scribario — AI Social Media Automation via Telegram",
    template: "%s — Scribario",
  },
  description:
    "Text what you want. AI creates 3 unique caption + image options. One tap publishes to Facebook. Social media on autopilot from Telegram.",
  metadataBase: new URL("https://scribario.com"),
  applicationName: "Scribario",
  keywords: [
    "social media automation",
    "AI social media",
    "social media management",
    "AI content creation",
    "Telegram bot",
    "social media posting",
    "automated posting",
    "AI captions",
    "AI images",
    "social media marketing",
    "content automation",
    "Facebook automation",
    "autopilot posting",
    "small business social media",
    "social media AI tool",
  ],
  authors: [{ name: "Scribario", url: "https://scribario.com" }],
  creator: "Scribario",
  publisher: "Scribario",
  openGraph: {
    title: "Scribario — AI Social Media Automation via Telegram",
    description:
      "AI social media automation via Telegram. Text your idea, get 3 publish-ready posts with captions and images, and publish to Facebook in 30 seconds — no tools, no agency.",
    url: "https://scribario.com",
    siteName: "Scribario",
    images: [
      {
        url: "/opengraph-image",
        width: 1200,
        height: 630,
        alt: "Scribario — AI-powered social media automation",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    site: "@scribario",
    creator: "@scribario",
    title: "Scribario — AI Social Media Automation via Telegram",
    description:
      "AI social media automation via Telegram. Text your idea, get 3 publish-ready posts with captions and images, and publish to Facebook in 30 seconds — no tools, no agency.",
    images: ["/opengraph-image"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: { canonical: "https://scribario.com" },
  manifest: "/manifest.json",
  other: {
    "theme-color": "#FF6B4A",
    "color-scheme": "light",
    "msapplication-TileColor": "#FF6B4A",
  },
  category: "technology",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="sitemap" type="application/xml" href="/sitemap.xml" />
        <link rel="preconnect" href="https://t.me" />
        <link rel="dns-prefetch" href="https://t.me" />

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

        {/* Organization + SoftwareApplication structured data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "Organization",
                  "@id": "https://scribario.com/#organization",
                  name: "Scribario",
                  url: "https://scribario.com",
                  logo: {
                    "@type": "ImageObject",
                    url: "https://scribario.com/icon-512",
                    width: 512,
                    height: 512,
                  },
                  sameAs: [
                    "https://t.me/ScribarioBot",
                    "https://facebook.com/scribario",
                  ],
                  contactPoint: {
                    "@type": "ContactPoint",
                    email: "privacy@scribario.com",
                    contactType: "customer support",
                  },
                },
                {
                  "@type": "WebSite",
                  "@id": "https://scribario.com/#website",
                  url: "https://scribario.com",
                  name: "Scribario",
                  publisher: {
                    "@id": "https://scribario.com/#organization",
                  },
                  inLanguage: "en-US",
                },
                {
                  "@type": "SoftwareApplication",
                  name: "Scribario",
                  applicationCategory: "BusinessApplication",
                  operatingSystem: "Web, Telegram",
                  description:
                    "AI-powered social media automation. Text what you want, AI creates 3 unique options, one tap publishes to Facebook — in 30 seconds.",
                  url: "https://scribario.com",
                  offers: {
                    "@type": "AggregateOffer",
                    lowPrice: "0",
                    highPrice: "99",
                    priceCurrency: "USD",
                    offerCount: "4",
                  },
                  publisher: {
                    "@id": "https://scribario.com/#organization",
                  },
                  featureList: [
                    "AI-generated social media captions",
                    "AI-generated images",
                    "AI-generated short-form video",
                    "Facebook publishing",
                    "Telegram bot interface",
                    "Brand voice customization",
                    "One-tap approval and posting",
                  ],
                },
              ],
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
