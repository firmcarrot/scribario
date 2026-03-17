import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Simple, transparent pricing for AI-powered social media automation. First 5 posts free, then upgrade when you're ready. Plans from $19 to $49/month.",
  alternates: { canonical: "https://scribario.com/pricing" },
  openGraph: {
    title: "Pricing — Scribario",
    description:
      "Simple, transparent pricing for AI-powered social media automation. Start free, upgrade when you're ready.",
    url: "https://scribario.com/pricing",
  },
};

const schemas = [
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://scribario.com" },
      { "@type": "ListItem", position: 2, name: "Pricing", item: "https://scribario.com/pricing" },
    ],
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: "What platforms do you support?",
        acceptedAnswer: { "@type": "Answer", text: "Facebook, Instagram, X (Twitter), LinkedIn, and more coming soon. Connect them all from inside Telegram." },
      },
      {
        "@type": "Question",
        name: "How does video generation work?",
        acceptedAnswer: { "@type": "Answer", text: "Text what you want — a product showcase, a promo reel, a behind-the-scenes clip. Our AI creates a 30-second video matched to your brand. Available on Pro ($5/video) and Business (5 included)." },
      },
      {
        "@type": "Question",
        name: "Can I cancel anytime?",
        acceptedAnswer: { "@type": "Answer", text: "Yes. No contracts, no cancellation fees. Your plan stays active until the end of your billing period." },
      },
      {
        "@type": "Question",
        name: "Do I need to install anything?",
        acceptedAnswer: { "@type": "Answer", text: "No. Everything happens inside Telegram. Just open the Scribario bot and start texting. Works on any phone, tablet, or desktop." },
      },
      {
        "@type": "Question",
        name: "What happens after my 5 free posts?",
        acceptedAnswer: { "@type": "Answer", text: "After your first 5 posts, you'll be prompted to choose a plan. Your connected platforms and brand voice settings stay saved — just pick a plan to keep posting." },
      },
      {
        "@type": "Question",
        name: "How is this different from Canva or Buffer?",
        acceptedAnswer: { "@type": "Answer", text: "Those tools still require you to design and schedule. Scribario does both — you text a message, we create the post and publish it. No editors, no calendars, no learning curve." },
      },
    ],
  },
];

export default function PricingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemas[0]) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemas[1]) }}
      />
      {children}
    </>
  );
}
