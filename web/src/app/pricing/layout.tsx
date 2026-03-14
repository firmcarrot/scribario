import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Simple, transparent pricing for AI-powered social media automation. Start free, upgrade when you're ready. Plans from $0 to $49/month.",
  alternates: { canonical: "https://scribario.com/pricing" },
  openGraph: {
    title: "Pricing — Scribario",
    description:
      "Simple, transparent pricing for AI-powered social media automation. Start free, upgrade when you're ready.",
    url: "https://scribario.com/pricing",
  },
};

export default function PricingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
