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
- **Deploy:** Vercel (serverless — NO static export, enables API routes)
- **Domain:** scribario.com
- **Port:** 3000 (Next.js default)

---

## TECH STACK

- Next.js 16 (App Router, serverless deployment)
- TypeScript strict
- Tailwind CSS v4
- Framer Motion
- Puppeteer (dev only — screenshot workflow)

---

## FRONTEND DESIGN QUALITY (MANDATORY — Anthropic Official Anti-Slop)

<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>

### Screenshot Evaluation Rules (from Anthropic Vision Best Practices)
- **Send screenshot BEFORE evaluation text** — image-then-text ordering produces better analysis
- **Label multiple screenshots explicitly** — use "Image 1:" / "Image 2:" between images
- **Think step-by-step before evaluating** — analyze every part of the image before giving feedback
- **Be explicit about exceptional quality** — every design brief must include "go beyond the basics"
- **Request animations by name** — they won't be added unless explicitly asked for

---

## BRAND SYSTEM (APPLE-CINEMATIC THEME — as of 2026-03-14)

**⚠️ OVERRIDES all previous themes. This plan SUPERSEDES existing CLAUDE.md and HARNESS.md design specs.**

| Token | Hex | Use |
|---|---|---|
| background | #FFFFFF | Main bg (white) |
| background_alt | #F5F5F7 | Apple's light gray — cards, alt sections |
| background_dark | #0A0A0F | Near-black cinematic — Proof, Feature showcase, FinalCTA |
| text | #000000 | Primary text (black) |
| text_dark | #1D1D1F | Text on light gray backgrounds |
| text_secondary | rgba(0,0,0,0.44) | Muted text |
| accent | #FF6B4A | Primary CTA — Coral Orange |
| accent_secondary | #0088CC | Telegram blue |
| accent_tertiary | #E5553A | Darker coral — body-size text on white (WCAG AA 4.6:1) |
| card_bg | #FFFFFF | Cards (white, revealed via clip-path) |
| separator | rgba(0,0,0,0.06) | Section dividers |
| faq_border | rgb(224,224,224) | FAQ accordion borders |

### Typography Scale (Apple-Level)

| Element | Size | Weight | Tracking |
|---------|------|--------|----------|
| Hero headline | `clamp(3.5rem, 7vw, 7rem)` | 700 | -0.04em |
| Section headline | `clamp(2.5rem, 5vw, 5rem)` | 700 | -0.03em |
| Feature headline | `clamp(1.75rem, 3vw, 3rem)` | 700 | -0.02em |
| Body large | `clamp(1.25rem, 2vw, 2rem)` | 400 | -0.01em |
| Body | `clamp(1rem, 1.2vw, 1.2rem)` | 400 | -0.01em |
| Label/mono | `0.75rem` | 400 | 0.1em |
| Stat number | `clamp(4rem, 8vw, 8rem)` | 700 | -0.04em |

**Fonts:** Clash Display (display), Cabinet Grotesk (body), JetBrains Mono (code)
**Voice:** Confident. Effortless. Direct.

---

## DESIGN PRINCIPLES (Apple-Cinematic Storytelling)

- **Typography as architecture** — Size, weight, color create structure. NOT cards or containers.
- **Apple-style light/dark rhythm** — White → light gray (#F5F5F7) → near-black (#0A0A0F) → white
- **Clip-path card reveals** — Keep for one key section (How It Works). Signature interaction.
- **Never same layout for consecutive sections** — Alternate centered/left/right/split/full-width
- **Staggered entrances** — Label → heading → body → CTA, with 0.08-0.12s delays (Framer Motion)
- **Scroll animations use custom RAF engine** — NOT Framer Motion useScroll
- **Stats count up** — Never appear statically, always animate in
- **Hero headings ~7vw** — Tight line-height (1.04), letter-spacing -0.04em
- **Section headings ~5vw** — Generous whitespace per section
- **Phone IS the hero** — Like Apple iPhone pages. 60% viewport, 3D perspective tilt, dramatic shadows
- **Generous spacing** — `clamp(6rem, 12vw, 12rem)` between sections
- **prefers-reduced-motion** — All scroll animations degrade gracefully

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
