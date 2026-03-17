import { Hero } from "@/components/sections/Hero";
import { PainPoints } from "@/components/sections/PainPoints";
import { Proof } from "@/components/sections/Proof";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { FeatureShowcase } from "@/components/sections/FeatureShowcase";
import { SocialProof } from "@/components/sections/SocialProof";
import { Demo } from "@/components/sections/Demo";
import { FinalCTA } from "@/components/sections/FinalCTA";
import { Footer } from "@/components/sections/Footer";

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "Is Scribario free to try?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. Open Telegram, search @ScribarioBot, and start texting. No signup, no credit card. You can create posts immediately and see exactly what you'll get before connecting any platforms.",
      },
    },
    {
      "@type": "Question",
      name: "Which platforms does it publish to?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Facebook, Instagram, LinkedIn, X (Twitter), TikTok, YouTube, Bluesky, Pinterest, and Threads. You can publish to all of them at once or say 'post to Instagram and Facebook only' — natural language targeting.",
      },
    },
    {
      "@type": "Question",
      name: "How is this different from Buffer or Hootsuite?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Those tools are dashboards that help you schedule content you've already created. Scribario creates the content for you — captions, images, video — and publishes it. There's no dashboard to learn. The entire workflow happens in a text conversation.",
      },
    },
    {
      "@type": "Question",
      name: "Can it match my brand's voice and style?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. Scribario learns from every post you approve. The more you use it, the better it understands your tone, vocabulary, and style preferences. You can also upload reference photos so your visuals stay consistent.",
      },
    },
    {
      "@type": "Question",
      name: "What about video content?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Scribario generates both short-form reels (8-second clips) and long-form video (15-60 seconds) with AI voiceover, sound effects, and your logo watermark. Just describe the video you want — same text conversation, same 30-second workflow.",
      },
    },
    {
      "@type": "Question",
      name: "Can I manage my social media from Telegram?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "That's the entire idea. Telegram is your interface — no app to download, no dashboard to learn. Text your bot, approve the content, and it's published. You can do it from your phone while standing in line at the grocery store.",
      },
    },
    {
      "@type": "Question",
      name: "What if I don't like the options?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Tap Edit and describe what you want changed — 'make it shorter,' 'add a question hook,' 'more professional tone.' You can also regenerate just one image without losing the caption you liked. Iterate until it's perfect.",
      },
    },
    {
      "@type": "Question",
      name: "Do I need to know anything about social media?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "No. Just describe what you want to post in plain English — 'promote our weekend brunch special' or 'announce our new listing at 123 Oak St.' Scribario handles the caption writing, image creation, hashtags, and formatting for each platform.",
      },
    },
  ],
};

export default function Home() {
  return (
    <main id="main-content">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <Hero />
      <PainPoints />
      <Proof />
      <HowItWorks />
      <FeatureShowcase />
      <SocialProof />
      <Demo />
      <FinalCTA />
      <Footer />
    </main>
  );
}
