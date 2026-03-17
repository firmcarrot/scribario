# Scribario Website Revamp — Video + Pricing + Showcase

## Context
Scribario now supports video generation (premium add-on, ~$5/video). Site needs:
1. Pricing page with tiered plans (Free/Pro/Business)
2. Showcase page with real output gallery (posts + videos)
3. Homepage updates to subtly mention video capability
4. Navbar updates for multi-page navigation

Target: Solopreneurs + small business owners. Premium positioning. Payments happen inside Telegram.

## Pages

### 1. Homepage (`/`) — Updates Only
- Hero copy: no change (social posts remain the headline)
- Industries/Demo section: add subtle "Posts & Videos" mention
- FinalCTA: add one line mentioning video as premium upgrade
- No major structural changes — the scroll story still works

### 2. Pricing Page (`/pricing`) — NEW
- Full dark bg (`bg-dark: #1A1A2E`)
- Massive heading: "Choose your / plan" (coral gradient on "plan")
- Monthly/Annual toggle (20% annual discount)
- 3 glassy cards side-by-side (stacked mobile):
  - Free ($0): 5 posts/mo, 1 platform
  - Pro ($19/mo, popular): Unlimited posts, all platforms, video $5/each
  - Business ($49/mo): Unlimited posts, all platforms, 5 videos included then $4/each
- Cards: backdrop-blur, semi-transparent bg, coral accents (not cyan)
- Pro card: scale-105, coral ring, "Most Popular" badge
- Video add-on callout line below cards
- FAQ accordion (5-6 questions)
- Bottom CTA → Telegram

### 3. Showcase Page (`/showcase`) — NEW
- White base with bg-alt alternating
- Massive heading: "See what / Scribario creates"
- Filter tabs: All, Social Posts, Videos, by industry
- Gallery grid (2-col desktop, 1-col mobile):
  - Each card: text input bubble + output image/video + tags + generation time
  - Video cards: play button overlay, "Pro feature" badge
- Dedicated video row (3-4 larger cards)
- Bottom CTA → Telegram

### 4. Navbar Updates
- Add "Showcase" and "Pricing" links
- Keep "Try it free →" CTA
- Mobile: small text links or hamburger menu

## Tech Stack (unchanged)
- Next.js 16 App Router, static export
- Tailwind v4, Framer Motion
- No shadcn, no external UI libs
- Components built native to existing design system

## Build Order
1. Navbar — add Showcase + Pricing links
2. Pricing page — `/pricing` route + PricingCard component
3. Showcase page — `/showcase` route + ShowcaseCard component
4. Homepage tweaks — subtle video mentions in Demo + FinalCTA
5. Full QA screenshots

## Design Tokens (existing, reused)
- Cards: backdrop-blur-[14px], bg rgba(255,255,255,0.06), border rgba(255,255,255,0.1)
- Popular badge: bg var(--accent), coral ring
- Check icons: var(--accent) coral
- Fonts: Clash Display (headings/prices), Cabinet Grotesk (body), JetBrains Mono (tags)
- All CTAs → t.me/ScribarioBot
