# Scribario SEO Configuration

## Favicon System

All favicons are dynamically generated via Next.js `ImageResponse` (edge runtime). Orange (#FF6B4A) rounded square with white bold "S".

| File | Size | Purpose |
|------|------|---------|
| `src/app/icon.tsx` | 32x32 | Browser tab favicon |
| `src/app/icon.svg` | 32x32 | SVG fallback |
| `src/app/apple-icon.tsx` | 180x180 | iOS home screen |
| `src/app/icon-192/route.tsx` | 192x192 | PWA manifest |
| `src/app/icon-512/route.tsx` | 512x512 | PWA manifest |

## Open Graph Image

`src/app/opengraph-image.tsx` — 1200x630 dynamic image. Dark bg (#1A1A2E), Scribario branding, headline, tagline, CTA button.

## Metadata

### Root Layout (`src/app/layout.tsx`)
- Title template: `%s — Scribario` (subpages inherit)
- Default title: "Scribario — Your social media team in a text"
- 18 keywords targeting AI social media automation
- GoogleBot: `max-image-preview: large`, `max-snippet: -1`, `max-video-preview: -1`
- Theme color: `#FF6B4A`

### Per-Page Metadata
| Page | Title | Has Canonical | Has Description |
|------|-------|---------------|-----------------|
| `/` | Default (from layout) | Yes | Yes |
| `/pricing` | "Pricing" (via layout.tsx) | Yes | Yes |
| `/terms` | "Terms of Service" | Yes | Yes |
| `/privacy` | "Privacy Policy" | Yes | Yes |

## Structured Data (JSON-LD)

Root layout contains `@graph` with three schemas:

1. **Organization** — Name, logo (512px icon), contact point, sameAs links
2. **WebSite** — URL, name, publisher reference
3. **SoftwareApplication** — Category, features list, aggregate offer ($0-$49)

## PWA Manifest

`public/manifest.json` — standalone display, coral theme, references `/icon-192` and `/icon-512` routes.

## Sitemap & Robots

- `src/app/sitemap.ts` — All 4 pages with priorities
- `src/app/robots.ts` — Allow all, sitemap link

## Security Headers

`vercel.json` — X-Frame-Options DENY, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.

## Manual Steps Required

1. **Google Search Console** — Verify domain, submit `https://scribario.com/sitemap.xml`
2. **Bing Webmaster Tools** — Same process
3. **Social profiles** — Create facebook.com/scribario, @scribario on X
4. **Google Business Profile** — Optional, for local SEO

## Audit Checklist

When running SEO audits, verify:
- [ ] All pages return unique `<title>` tags
- [ ] All pages have unique meta descriptions
- [ ] All pages have canonical URLs
- [ ] OG image renders at `/opengraph-image` (check with social debuggers)
- [ ] Favicon shows orange S in browser tab
- [ ] `/sitemap.xml` lists all pages
- [ ] `/robots.txt` allows crawling
- [ ] Structured data validates at schema.org/validator
- [ ] Lighthouse SEO score ≥ 95
