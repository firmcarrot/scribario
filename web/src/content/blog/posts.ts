export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  keywords: string[];
  readingTime: string;
  body: string;
}

export const posts: BlogPost[] = [
  {
    slug: "how-to-automate-social-media-posts",
    title: "How to Automate Social Media Posts Without Losing Your Voice",
    description:
      "Most automation tools post generic content. Here's how AI-powered automation creates original, brand-matched posts — no templates, no slop.",
    date: "2026-03-14",
    author: "Scribario Team",
    keywords: ["how to automate social media posts", "social media automation", "AI social media"],
    readingTime: "5 min read",
    body: `Social media automation has a reputation problem. When most people hear "automated posts," they picture generic, templated content that screams "a robot wrote this."

That reputation is earned. Most automation tools — Buffer, Hootsuite, Later — automate the *scheduling* part, not the *creation* part. You still write the caption. You still design the image. You still resize for each platform. The tool just posts it at a time you picked.

That's not automation. That's a timer.

## What real automation looks like

Real automation means you describe what you want to post — in plain English — and the AI handles everything else:

- **Caption writing** with five different formula types (Hook-Story-Offer, PAS, Punchy, Story-Lesson, List/Value Drop)
- **Image generation** matched to your brand's visual style
- **Platform formatting** — right dimensions, hashtag counts, and character limits for each network
- **Publishing** to all your connected platforms with one tap

The entire workflow takes 30 seconds. Not 30 minutes of design + writing + scheduling.

## The brand voice problem

The biggest fear with AI content is losing your brand voice. If every post sounds like ChatGPT, you've traded one problem (no time to post) for another (generic content that doesn't sound like you).

Scribario solves this with **brand voice learning**. Every post you approve becomes a reference example. The AI studies your approved content — your vocabulary, your tone, your sentence structure — and uses it to generate future posts that sound like you, not like a robot.

After 10-15 approved posts, the difference is dramatic. The AI starts using your specific phrases, matching your level of formality, and even adopting your humor style.

## Three options, not one

Instead of generating one caption and hoping you like it, Scribario generates three completely different options for every request. Each uses a different writing formula:

1. **A hook-story-offer post** that grabs attention, tells a micro-story, and drives action
2. **A punchy one-liner** that works for quick, scroll-stopping content
3. **A value-driven list** that provides information and builds authority

You pick the one that feels right. Or you tap Edit and say "make option 2 shorter and add a question hook." The AI revises while keeping your brand voice intact.

## The bottom line

Social media automation shouldn't mean "schedule your manually-created content." It should mean "describe what you want and get it done." That's the difference between tools that manage content and tools that create it.

If you're spending more than 30 seconds per post, you're doing it the old way.`,
  },
];
