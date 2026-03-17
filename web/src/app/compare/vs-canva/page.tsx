import { Metadata } from "next";
import { comparisons } from "@/content/comparisons";
import { ComparisonPageTemplate } from "@/components/sections/ComparisonPageTemplate";
import { Footer } from "@/components/sections/Footer";

const data = comparisons["vs-canva"];

export const metadata: Metadata = {
  title: data.metaTitle,
  description: data.metaDescription,
  alternates: { canonical: `https://scribario.com/compare/${data.slug}` },
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "Compare", item: "https://scribario.com/compare" },
    { "@type": "ListItem", position: 3, name: "vs Canva", item: "https://scribario.com/compare/vs-canva" },
  ],
};

export default function VsCanvaPage() {
  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      <ComparisonPageTemplate comparison={data} />
      <Footer />
    </main>
  );
}
