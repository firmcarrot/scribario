import { Metadata } from "next";
import { niches } from "@/content/niches";
import { NichePageTemplate } from "@/components/sections/NichePageTemplate";
import { Footer } from "@/components/sections/Footer";

const niche = niches.restaurants;

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
    { "@type": "ListItem", position: 3, name: "Restaurants", item: "https://scribario.com/for/restaurants" },
  ],
};

export default function RestaurantsPage() {
  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <NichePageTemplate niche={niche} />
      <Footer />
    </main>
  );
}
