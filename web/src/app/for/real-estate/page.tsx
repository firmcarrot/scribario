import { Metadata } from "next";
import { niches } from "@/content/niches";
import { NichePageTemplate } from "@/components/sections/NichePageTemplate";
import { Footer } from "@/components/sections/Footer";

const niche = niches["real-estate"];

export const metadata: Metadata = {
  title: niche.metaTitle,
  description: niche.metaDescription,
  alternates: { canonical: `https://scribario.com/for/${niche.slug}` },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "Industries", item: "https://scribario.com/for" },
    { "@type": "ListItem", position: 3, name: "Real Estate", item: "https://scribario.com/for/real-estate" },
  ],
};

export default function RealEstatePage() {
  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <NichePageTemplate niche={niche} />
      <Footer />
    </main>
  );
}
