import { Metadata } from "next";
import { AboutContent } from "./AboutContent";
import { Footer } from "@/components/sections/Footer";

export const metadata: Metadata = {
  title: "About Scribario — AI Social Media Automation via Telegram",
  description:
    "Scribario turns a Telegram text into publish-ready social media content. Built on Claude AI, Nano Banana 2, and Veo 3.1. Currently publishing to Facebook, with more platforms coming soon.",
  alternates: { canonical: "https://scribario.com/about" },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "About", item: "https://scribario.com/about" },
  ],
};

export default function AboutPage() {
  return (
    <main id="main-content">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <AboutContent />
      <Footer />
    </main>
  );
}
