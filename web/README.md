# Scribario — Marketing Website

The public-facing marketing site for [Scribario](https://scribario.com), deployed on Vercel.

**Live:** [scribario.com](https://scribario.com) · **Preview:** [scribario-web.vercel.app](https://scribario-web.vercel.app)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Next.js 16](https://nextjs.org/) (App Router, static export) |
| Language | TypeScript (strict mode) |
| Styling | [Tailwind CSS v4](https://tailwindcss.com/) |
| Animations | [Framer Motion](https://www.framer.com/motion/) + custom RAF scroll engine |
| Fonts | Clash Display (headings), Cabinet Grotesk (body), JetBrains Mono (code) |
| Hosting | [Vercel](https://vercel.com/) (Hobby tier) |
| Domain | scribario.com via Namecheap DNS |

---

## Pages

| Route | Description |
|---|---|
| `/` | Homepage — hero with sticky phone demo, social proof, how-it-works, industry showcase, conversion CTA |
| `/pricing` | Pricing tiers (Free / Pro / Business) with 3D tilt cards, FAQ accordion, billing toggle |
| `/privacy` | Privacy policy |
| `/terms` | Terms of service |

---

## Architecture

### Scroll Engine (`src/lib/scroll-engine.ts`)

Custom `requestAnimationFrame`-based scroll manager. Components register scroll handlers via `getScrollEngine().register(id, callback)` instead of using Framer Motion's `useScroll`. This ensures:

- Single RAF loop for all scroll animations (no competing requestAnimationFrame calls)
- Helpers for interpolation (`iLerp`), clamping (`lerp`), and easing (`ease`)
- Clean registration/unregistration lifecycle tied to React `useEffect`

### Sticky Phone Demo

The hero and final CTA sections feature a phone composite (hand image + video overlay) that sticks during scroll. The phone uses:

- CSS `position: sticky` with a tall scroll zone (280vh hero, 200vh CTA)
- 3D perspective tilt animation driven by scroll position
- `IntersectionObserver` to ensure only one video plays at a time (prevents mobile OOM)
- Mobile fallback: static poster image, no video (iOS autoplay limits)

### Dark Section Detection (Navbar)

The navbar auto-switches between light and dark text using `data-dark` attributes on sections. A `MutationObserver` re-queries dark sections on App Router page transitions so the detection works across routes.

### Component Structure

```
src/
├── app/                    # Next.js pages
│   ├── page.tsx            # Homepage composition
│   ├── pricing/page.tsx    # Pricing with 3D tilt cards
│   ├── privacy/page.tsx    # Privacy policy
│   └── terms/page.tsx      # Terms of service
├── components/
│   ├── sections/           # Homepage sections (Hero, Proof, HowItWorks, Demo, FinalCTA, Footer)
│   ├── telegram/           # Telegram chat mockup animation system
│   └── ui/                 # Shared UI (Navbar, CardStack, CountUp, LegalSection)
├── data/                   # Conversation scripts for chat animation
├── hooks/                  # useConversationPlayer, useScrollProgress
├── lib/                    # Scroll engine
└── types/                  # TypeScript types
```

---

## Brand System

| Token | Value | Use |
|---|---|---|
| `--bg` | `#FFFFFF` | Main background |
| `--bg-alt` | `#F5F5F5` | Alternating sections |
| `--bg-dark` | `#1A1A2E` | Dark zones (demo, CTA, footer) |
| `--accent` | `#FF6B4A` | Primary CTA — coral orange |
| `--accent-secondary` | `#0088CC` | Telegram blue |
| `--text` | `#000000` | Primary text |
| `--text-secondary` | `rgba(0,0,0,0.62)` | Muted text (WCAG AA compliant) |

Typography: massive headings (up to 15vw), tight letter-spacing (-0.0575em), gradient text via `background-clip: text`.

---

## Development

```bash
cd web
npm install
npm run dev          # http://localhost:3000
npm run build        # Production build
```

### Screenshots (visual QA)

```bash
node scripts/screenshot.mjs                # Full page, desktop + mobile
node scripts/screenshot.mjs --viewport     # Above the fold only
node scripts/screenshot.mjs --section hero # Specific section
node scripts/screenshot.mjs --url /pricing # Different page
```

Requires Puppeteer (dev dependency). Screenshots save to `tmp_screenshots/` (gitignored).

---

## Deployment

### Vercel

The site deploys automatically from the `web/` subdirectory of this repo.

- **Project:** `scribario-web` on Vercel (under `ron-nadelbergs-projects`)
- **Root directory:** `web`
- **Framework:** Next.js (auto-detected)
- **Build command:** `next build` (default)
- **Production branch:** `main`
- **Preview branch:** `dev`

Manual deploy via CLI:

```bash
cd web
vercel deploy --prod --token $VERCEL_TOKEN
```

### DNS (Namecheap → Vercel)

| Type | Host | Value |
|---|---|---|
| A Record | `@` | `76.76.21.21` |
| CNAME | `www` | `cname.vercel-dns.com` |
| A Record | `postiz` | `31.97.13.213` (Postiz server — separate) |

SSL is auto-provisioned by Vercel.

### Environment Variables

No environment variables required for the marketing site. The Vercel deployment token is stored in the root `.env` file for CLI deploys:

```
VERCEL_TOKEN=your-vercel-token
```

---

## Design Principles

- **Typography as architecture** — size, weight, and color create visual hierarchy, not cards or borders
- **Color zones** — background shifts between sections: white → dark → white → alt → dark
- **Never repeat layouts** — consecutive sections alternate between centered, left-aligned, right-aligned, split
- **Scroll-driven storytelling** — sticky elements, text overlays, and progressive reveals
- **Mobile-first** — all components scale down gracefully; scroll animations disabled below 750px
- **Performance** — single RAF loop, lazy video loading, WebP images, preloaded fonts
