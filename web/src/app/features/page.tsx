import { Metadata } from "next";
import { FeaturesContent } from "./FeaturesContent";
import { Footer } from "@/components/sections/Footer";

export const metadata: Metadata = {
  title: "Features — AI Content Creation for Social Media | Scribario",
  description:
    "AI captions, images, video, 9-platform publishing, brand voice learning, scheduling — all from a Telegram text. See everything Scribario does.",
  alternates: { canonical: "https://scribario.com/features" },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "Features", item: "https://scribario.com/features" },
  ],
};

export default function FeaturesPage() {
  return (
    <main id="main-content">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <FeaturesContent />
      <Footer />
    </main>
  );
}
