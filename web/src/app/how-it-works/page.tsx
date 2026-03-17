import { Metadata } from "next";
import { HowItWorksContent } from "./HowItWorksContent";
import { Footer } from "@/components/sections/Footer";

export const metadata: Metadata = {
  title: "How Scribario Works — Auto Post to Social Media via Telegram",
  description:
    "Text what you want to post in Telegram. Get three AI-generated options with captions and images. Approve one. Published to all platforms in 30 seconds.",
  alternates: { canonical: "https://scribario.com/how-it-works" },
};

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "How long does it really take?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "From text to published post: 30 seconds if you approve the first option. 1-2 minutes if you want to edit or iterate. Compare that to the 40+ minute workflow most people use with design tools and schedulers.",
      },
    },
    {
      "@type": "Question",
      name: "Do I need to download an app?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "No. Telegram is available on iOS, Android, Windows, Mac, and Linux. If you already have Telegram, you can start using Scribario in 10 seconds. If not, download Telegram (free) and search for @ScribarioBot.",
      },
    },
    {
      "@type": "Question",
      name: "What if my brand voice changes over time?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Scribario learns from every post you approve. As your voice evolves, the AI adapts. You can also update your brand profile anytime with /brand — change your tone, audience, or content preferences.",
      },
    },
    {
      "@type": "Question",
      name: "Can I manage multiple brands?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes, on the Business plan. Each brand has its own voice profile, style settings, and connected platforms. Switch between brands within the same Telegram conversation.",
      },
    },
    {
      "@type": "Question",
      name: "What happens if I don't like any of the three options?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Tap Regenerate to get three entirely new options. Or edit any option with specific feedback — 'more formal,' 'add a call-to-action,' 'different image style.' You're never stuck with what the AI gives you first.",
      },
    },
  ],
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
    { "@type": "ListItem", position: 2, name: "How It Works", item: "https://scribario.com/how-it-works" },
  ],
};

export default function HowItWorksPage() {
  return (
    <main id="main-content">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <HowItWorksContent />
      <Footer />
    </main>
  );
}
