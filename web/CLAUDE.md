# SCRIBARIO WEB — Project Rules

## ⛔ HARNESS.md IS THE LAW — READ IT FIRST ⛔

**Before writing ANY code in this project, read `HARNESS.md` in the project root.**
**Every build loop step, every anti-laziness rule, every quality gate is MANDATORY.**
**If you haven't read HARNESS.md this session, read it NOW before doing anything.**

On 2026-03-12, Claude Code:
- Invoked skills as checkboxes (invoke → immediately dismiss)
- Wrote 7+ files in one batch without building or screenshotting
- Never took a single screenshot
- Ignored every rule in this file
- Produced the ugliest site Ron has ever seen
- Then tried to do it AGAIN the same way after being told to start over

**This resulted in Ron's explicit instruction: the HARNESS.md exists to prevent this from EVER happening again. If you skip any step, Ron will know — because the screenshots won't exist and the approval checkpoints won't have happened.**

## VISUAL WORK GATE (MANDATORY — NON-NEGOTIABLE)

Before writing or modifying ANY .tsx/.css component file:

1. **Have you read HARNESS.md this session?** If NO → read it NOW
2. **Has `brainstorming` skill been invoked AND fully engaged?** If NO → invoke it NOW (see HARNESS.md for minimum engagement requirements)
3. **Has `frontend-design` skill been invoked AND fully engaged?** If NO → invoke it NOW (see HARNESS.md for minimum engagement requirements)
4. **After building: has a screenshot been taken, READ, and evaluated?** If NO → do it NOW
5. **Has Ron explicitly approved the output?** If NO → present it and WAIT

Skipping any step = delete the code and start over.

---

## SCREENSHOT WORKFLOW (MANDATORY)

Use Puppeteer to visually verify work. Screenshots go to `tmp_screenshots/` (gitignored).

### Commands
```bash
# Full page — desktop + mobile
node scripts/screenshot.mjs

# Viewport only (above the fold)
node scripts/screenshot.mjs --viewport

# Specific section
node scripts/screenshot.mjs --section hero

# Different page
node scripts/screenshot.mjs --url /getting-started
```

### When to Screenshot
- **After building any section** — screenshot it, read the image, verify it looks good
- **Before declaring done** — full page screenshot of every page
- **When comparing to a reference** — screenshot both and compare
- **After any visual change** — verify the change looks correct

### Two-Pass Review
After building a page or major section:
1. Take full-page screenshots (desktop + mobile)
2. Read each screenshot and list specific issues
3. Fix issues
4. Take new screenshots and verify fixes
5. Only then declare the section done

---

## REFERENCE SITE WORKFLOW

When rebuilding or designing a page:

1. **Find inspiration** — Browse godly.website, awwwards.com, dribbble.com, or 21st.dev
2. **Extract HTML** — Use an HTML extractor tool or F12 → Elements → copy outerHTML to get the structure/styles of a reference site
3. **Save reference screenshots** — Full-page screenshots of reference sites go in `reference_screenshots/`
4. **Clone structure first, then rebrand** — Match the layout rhythm and spacing of the reference, then apply Scribario brand colors/fonts/copy
5. **Compare side by side** — Screenshot your build and the reference, compare section by section

### Individual Component Polish (21st.dev)
For specific components (backgrounds, buttons, hero animations, card hover effects):
- Browse https://21st.dev for components
- Copy the component code/prompt
- Tell Claude Code to integrate it into a specific section
- If the component is animated, skip screenshot comparison (animations don't screenshot well)

---

## IMAGE GENERATION (Nano Banana Skill)

When generating demo images or hero visuals:
- Use the `nano-banana-images` skill
- Minimum 2K resolution
- 16:9 for hero/backgrounds, 4:5 for social media demo images
- Clean backgrounds (nothing touching edges) for compositing on the site
- Generate 4 iterations minimum — spar with it, pick the best
- Reference previous images when generating variants (assembled → exploded technique)

---

## PROJECT IDENTITY

- **Product:** Scribario — AI social media automation via Telegram
- **Site type:** Marketing website + Getting Started guide
- **Deploy:** Vercel (static export)
- **Domain:** scribario.com
- **Port:** 3000 (Next.js default)

---

## TECH STACK

- Next.js 16 (App Router, static export)
- TypeScript strict
- Tailwind CSS v4
- Framer Motion
- Puppeteer (dev only — screenshot workflow)

---

## BRAND SYSTEM (CORAL-ORANGE THEME — as of 2026-03-12)

**⚠️ OVERRIDES previous green/dark theme. See HARNESS.md for enforcement.**

| Token | Hex | Use |
|---|---|---|
| background | #FFFFFF | Main bg (white) |
| background_alt | #F5F5F5 | Alt sections (near-white) |
| background_dark | #1A1A2E | Deep Navy dark zone (Demo section) |
| text | #000000 | Primary text (black) |
| text_secondary | rgba(0,0,0,0.44) | Muted text |
| accent | #FF6B4A | Primary CTA — Coral Orange |
| accent_secondary | #0088CC | Telegram blue |
| accent_tertiary | #E5553A | Darker coral for hover states |
| card_bg | #FFFFFF | Cards (white, revealed via clip-path) |
| separator | rgba(0,0,0,0.06) | Section dividers |
| faq_border | rgb(224,224,224) | FAQ accordion borders |

**Fonts:** Clash Display (display), Cabinet Grotesk (body), JetBrains Mono (code)
**Voice:** Confident. Effortless. Direct.

---

## DESIGN PRINCIPLES (adapted for light theme — ForHims-inspired)

- **Typography as architecture** — Size, weight, color create structure. NOT cards or containers.
- **Clip-path card reveals** — Cards open from `inset(0 64px round 45px)` to full on scroll. This is the signature interaction.
- **Color zones shift between sections** — white (#FFF) → near-white (#F5F5F5) → dark accent zone (#1A1A2E) → white
- **Never same layout for consecutive sections** — Alternate centered/left/right/split/full-width
- **Staggered entrances** — Label → heading → body → CTA, with 0.08-0.12s delays (Framer Motion)
- **Scroll animations use custom RAF engine** — NOT Framer Motion useScroll. See HARNESS.md animation boundary.
- **Stats count up** — Never appear statically, always animate in
- **Hero headings ~5.625vw** — Tight line-height (1.04), letter-spacing -0.0575em (see extraction doc for exact value)
- **Section headings ~15vw** — Massive, ForHims-scale
- **Gradient text everywhere** — background-clip: text with coral-orange/blue gradients
- **One scroll-stopping element** — The animated Telegram conversation in a sticky phone IS the scroll stopper
- **Generous spacing** — 17.36vw between sections, 64px side margins on cards

---

## GIT

- Branch: `main`
- Commit with feat/fix/chore prefix
- Don't push unless Ron says "push" or "create PR"

---

## FILE STRUCTURE

```
scribario-web/
├── CLAUDE.md              ← this file
├── brand_assets/          ← logo, brand guidelines
├── reference_screenshots/ ← inspiration site screenshots
├── public/
│   ├── fonts/             ← self-hosted WOFF2
│   └── images/demo/       ← demo images (Nano Banana generated)
├── scripts/
│   └── screenshot.mjs     ← Puppeteer screenshot tool
├── src/
│   ├── app/               ← Next.js pages
│   ├── components/
│   │   ├── sections/      ← homepage sections
│   │   ├── telegram/      ← chat animation system
│   │   └── ui/            ← shared UI components
│   ├── data/              ← conversation scripts
│   ├── hooks/             ← React hooks
│   └── types/             ← TypeScript types
└── tmp_screenshots/       ← gitignored, Puppeteer output
```
