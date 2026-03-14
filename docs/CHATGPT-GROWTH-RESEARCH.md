# Scribario — ChatGPT Deep Research: AI-Driven Marketing Playbook

**Source:** ChatGPT Deep Research, March 13, 2026
**Purpose:** Raw research output for first 100 paying users. To be integrated with GROWTH-STRATEGY.md.

---

## Executive Summary

Fastest path to 100 paying users = three always-on automated engines:
1. **Outbound email engine** (AI-personalized cold email → "text to demo" CTA)
2. **Inbound ad engine** (Google Search + Meta lead forms → SMS/Telegram nurture → checkout)
3. **Referral/affiliate engine** (in-product referral loop + creator seeding)

All unified through a single **text-first conversational funnel**.

---

## Ranked Tactics (Top 8)

| Rank | Tactic | Speed | Cost | ROI Potential |
|---|---|---|---|---|
| 1 | AI-personalized cold email → text-to-demo | Very fast | Low-Medium | High |
| 2 | Google Search intent capture → SMS/Telegram demo | Fast | Medium-High | Medium-High |
| 3 | Meta lead ads → instant SMS nurture → checkout | Fast | Medium-High | Medium |
| 4 | Viral "Text your business → get a week of posts" public number | Medium | Low | Very High (if it clicks) |
| 5 | In-product referral loop + credits/cashback | Medium | Low | Very High |
| 6 | Affiliate + micro-creator seeding with auto payout | Medium | Low-Medium | High |
| 7 | Agency/consultant reseller motion | Medium-Slow | Low | High |
| 8 | Programmatic SEO + social distribution → retargeting | Slow initial | Low-Medium | Very High long-term |

---

## Tactic 1: Cold Email → Text-to-Demo (FASTEST)

**Target:** Narrow wedge vertical (plumbers, roofers, med spas, real estate agents)
**CTA:** "Text START to [number] → get 7 done-for-you posts in 2 minutes"

**Funnel math (benchmarked):**
- Cold email reply rate: ~5.8% average
- Replies → texted demo: 20-40%
- Text demo → trial: 30-60%
- Trial → paid: ~17% (opt-in) or ~51% (opt-out)
- **10,000 emails → ~12 paid users** (conservative)
- Need ~60-100K targeted emails for 100 users

**Engineering effort:** 4-8 days MVP, 2-4 weeks durable
**Cost:** Email infra + domains + lead data (variable)

**Email template:**
```
Subject: Quick idea for {BusinessName}'s social posts

{FirstName} — quick one.

I noticed {PersonalizationObservation}. Most owners I talk to
don't have time to "learn a tool" after work.

Text "START" to {DemoNumber} and I'll generate a full week of
posts for {BusinessName} (captions + images + posting plan).
No login. No dashboard. Just text → done.

— Ron
```

---

## Tactic 2: Google Search → Text Funnel

**Target keywords:** "social media for plumbers," "marketing automation for contractors," "done for you social posts"
**CTA:** Same text-to-demo flow

**Benchmarks:** Google Ads CTR ~6.42%, conversion rate ~6.96%, CPL ~$66.69

**Engineering effort:** 1-2 weeks MVP
**Cost:** Primarily ad spend

---

## Tactic 3: Meta Lead Ads → SMS Nurture

**Flow:** Lead form → SMS within 60 seconds → demo pack → checkout link
**Key:** Speed matters — contact within 1 minute of form submission

**Engineering effort:** 5-10 days MVP
**Cost:** Ad spend driven

---

## Tactic 4: Viral Public Number + Watermark Loop

**Flow:**
1. User texts business name + what they do
2. System generates 3 posts + images
3. Posts include "Made by Scribario" watermark + referral code
4. User shares → friends text START → loop repeats

**Viral coefficient:** invites_per_user × acceptance_rate > 1 = self-sustaining growth

**Engineering effort:** 3-7 days MVP
**Cost:** LLM generation + messaging costs only

---

## Tactic 5: In-Product Referral Loop

**Trigger:** Right after Scribario publishes a post (value moment)
**Message:** "Want a free week? Forward this: {ref_link} (you both get $X credit)"
**Research:** Referred customers ~16% higher lifetime value

**Abuse controls:** Max 10 rewards/mo, unique payment method required, clawback on refund

---

## Tactic 6: Affiliate/Creator Seeding

**Target:** Micro-creators in local business / SMB growth niches
**Flow:** Auto-discover → outreach → provision demo account → send creator kit → track → auto-payout
**Commission:** Recurring rev share via Stripe Connect

---

## Tactic 7: Agency Reseller Motion

**Target:** Agencies already managing SMB marketing
**Pitch:** "Add text-to-marketing as a productized service for your clients"
**Flow:** Auto-generated co-branded landing pages + split payments

---

## Tactic 8: Programmatic SEO

**Generate thousands of pages:**
- "AI social media for restaurants in Houston"
- "AI Instagram for salons in Miami"
- "Automated social posts for food trucks in Austin"

**Each page:** Unique content + single CTA ("Text START to...")
**Timeline:** Slowest to start, strongest compounding

---

## SMS/Telegram Demo Flow Script

```
SYSTEM: Send your business name + what you do + city.
USER: Apex Plumbing, water heaters + drain cleaning, Phoenix

SYSTEM: Pick your vibe:
1) Helpful expert
2) Funny + friendly
3) Straight-to-the-point
Reply 1/2/3.

USER: 1

SYSTEM: Any promos this week? (Or reply "skip")
USER: $49 drain inspection

SYSTEM: Here are 3 posts ready to publish:
POST 1: ...
POST 2: ...
POST 3: ...

Want us to do this every week and auto-post it? Reply GO.
(Price: $59/mo, cancel anytime)
```

---

## LLM Prompt Templates (Automation-Ready)

### Intake (extract business context)
```json
{
  "role": "user",
  "content": "Message: {{RAW_USER_TEXT}}\nReturn JSON: business_name, vertical, city, services, promo, tone, target_customer"
}
```

### Cold Email Personalization
```json
{
  "role": "user",
  "content": "Create ONE sentence opener for cold email. Use only facts provided.\nFacts: {{LEAD_FACTS_JSON}}\nRules: no exaggeration, no guessing.\nOutput: {\"opener\":\"...\"}"
}
```

### Reply Classifier
```json
{
  "role": "user",
  "content": "Classify intent: interested, question, not_interested, wrong_person, ooto, spam_complaint, stop.\nMessage: {{INBOUND_TEXT}}\nOutput: {\"intent\":\"...\",\"confidence\":0-1,\"suggested_reply\":\"...\"}"
}
```

---

## Ad Copy Templates

### Google Search Headlines
1. Marketing by Text Message
2. Replace Your Marketing Dept With a Text
3. Social Posts Done For You Weekly
4. No Dashboard. No Templates. Just Text.

### Meta Primary Text
1. You're not "bad at marketing." You're just tired. Text your business → we make the posts.
2. If Canva feels like homework, you're our kind of person. Text → we handle everything.
3. Small business owners: want your social handled without a dashboard? Text us. Done.

---

## Landing Page Copy

```
H1: Replace your marketing department with a text message.
Subhead: Send one text. Scribario creates your posts, images/videos, and schedules them.

What you get:
- Weekly posts tailored to your business
- Captions + hashtags + CTAs
- Images/video scripts
- Auto-scheduling across your socials

CTA: Text START to {DemoNumber}
Secondary: Or try in Telegram: @ScribarioBot

Trust: "No dashboard to learn." / "Cancel anytime." / "Built for busy owners."
```

---

## Compliance Guardrails

- **Email:** CAN-SPAM — opt-out links, physical address, no deceptive subjects, honor unsubscribes
- **SMS:** TCPA — user-initiated or explicit written consent only. NO cold SMS blasts.
- **LinkedIn:** Explicitly bans third-party automation. Ads/official APIs only.
- **Content claims:** No medical, legal, or financial guarantees in AI-generated copy.

---

## Recommended Automation Stack

| Component | Tool |
|---|---|
| Data + state | Supabase + pg_cron |
| SMS | Twilio |
| Chat | Telegram bot (existing) |
| Posting | Postiz API (existing) |
| LLM | Claude API (existing) |
| Paid ads | Meta Marketing API + Google Ads API |
| Payments | Stripe + Connect for affiliates |
| No-code glue | Zapier/Make (optional) |

---

## Key Benchmarks for Forecasting

| Metric | Benchmark |
|---|---|
| Cold email reply rate | ~5.8% average |
| SaaS landing conversion | ~3.8% median |
| Opt-in trial → paid | ~17% |
| Opt-out trial → paid | ~51% |
| Google Ads CTR | ~6.42% |
| Google Ads conversion rate | ~6.96% |
| Google Ads avg CPL | ~$66.69 |
| Referred customer value uplift | ~16% higher LTV |
