# ForHims App Site — Full Design Extraction

**Source:** https://app.forhims.com/?ref=godly
**Extracted:** 2026-03-12

---

## 1. CSS Custom Properties

No CSS custom properties used. All values hard-coded in rules.

---

## 2. HTML Structure (Body)

```
body
  #app
    nav#nav (fixed, transparent, z-index:4)
      a#nav-logo (two SVG logos — black + white, toggled by .fx class)
      a.soon (CTA: "Download now", pill button, absolute top-right)
    header#hero
      div.card
        div.card-shadow
        div.card-content (clip-path animated on scroll, bg image)
          div#hero-card-content-gradient (radial gradient blob overlay)
          img (hero bg image)
          h1 "Total care. Totally different."
          div.card-content-phone-shim
          div.card-content-phone-sticky (sticky phone mockup)
          div.card-content-list (scroll-animated list items)
      div#hero-txt (massive bg text: "it's all / in / the app")
      div.p (hero paragraph — gradient text)
    div.separator
    div#intro
      ul#intro-list ("Care", "Programs", "Shop")
      div#intro-img (img)
      p (intro paragraph)
    section#program .section
      div.section-rectangle (SVG)
      h2 "Programs"
      div.card
        div.card-shadow
        div.card-content
          div#program-card-content-percent-w (animated percentage circle)
          div#program-card-content-intro (gradient text span)
          div#program-card-content-grid (img)
          div.card-content-phone-shim
          div.card-content-phone-sticky
          div.card-content-list > ul.card-content-list-sticky
      div.p (section copy)
    section#care .section
      div.section-rectangle (SVG)
      h2 "Care"
      div.card (black bg variant)
        div.card-content
          div#care-card-0 (text + phone img)
          div#care-card-1 (icon + text, gradient bg)
          div#care-card-2 (half-speed scroll images)
      div.p (section copy)
    section#shop .section
      div.section-rectangle (SVG)
      h2 "Member Shop"
      div.card
        div#shop-card-bg
        div.card-content
          div#shop-card-content-grid (img)
          div.card-content-phone-shim
          div.card-content-phone-sticky
          div.card-content-list > ul.card-content-list-sticky
      div.p (section copy)
    div.separator
    div#video
      div#video-center-logo-square (SVG)
      svg#video-center-logo
      a.soon "Download now"
    section#faq
      h2 "Hims App FAQs"
      ul (4 FAQ items with accordion)
    footer
      div#footer-top (logo + links)
      ul#footer-center (legal links)
      div#footer-bottom (copyright)
```

---

## 3. Animation / Transition CSS

### @keyframes
None from page CSS. All animation is JS/RAF driven.

### Transition Rules
```css
#nav-logo div {
  transition: opacity 0.2s cubic-bezier(0.215, 0.61, 0.355, 1);
}
.faq-list-arrow {
  transition: transform 0.6s cubic-bezier(0.19, 1, 0.22, 1);
}
.faq-li.on .faq-list-arrow {
  transform: rotate(180deg);
}
```

### Transform Rules
```css
.card-content-phone { transform: translateY(-50%); }
.card-content-phone > img, .card-content-screen { transform: translate(-50%, -50%); }
#program-card-content-percent-line { transform: rotate(-90deg); }
#care-card-0-phone img { transform: translate(-50%, -50%); }
#program-card-content-grid img { transform: translateX(-50%); }
#shop-card-content-grid img { transform: translateX(-50%); }
.clip img { transform: translateX(-50%); }
#hero-card-content-gradient::after { transform: translate(-50%, -50%); }
```

### will-change (scroll performance hints)
```css
#nav-logo div              { will-change: opacity; }
.card-content              { will-change: clip-path; }
.card-content-list-sticky-copy { will-change: transform, opacity; }
#hero-card-content-gradient { will-change: opacity; }
```

### JS-Driven Animation Engine
- No GSAP, AOS, Lenis, ScrollTrigger, or LocomotiveScroll
- Custom RAF engine: `window.R` (with R.Raf, R.Lerp, R.LerpM, R.iLerp, R.Remap, R.Clamp, R.Ease)
- App state: `window._A: { s: <scrollY>, needS, engine, isMobile, win: {w, h} }`
- Scroll engine components: shim, clip, programPercent, list, heroGradient, navColor
- **Clip-path animation** on `.card-content` — cards open from inset as you scroll
- **List fade/slide** — `.card-content-list-sticky-copy` animates via lerp
- **Hero gradient fade** — opacity controlled by scroll position
- **Nav logo swap** — `.fx` class toggles black/white based on background

---

## 4. Typography Stack

Single font: **Sofia Pro** (sofia), system fallback only in browser extensions.

```css
@font-face {
  font-family: sofia;
  src: url("/font/SofiaProMedium.woff2") format("woff2");
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: sofia;
  src: url("/font/SofiaProRegular.woff2") format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}
```

| Context | Size | Weight | Line-height | Letter-spacing | Color |
|---------|------|--------|-------------|----------------|-------|
| body base | 16px | 500 | normal | normal | — |
| h1 hero | 5.625vw (86.68px) | 500 | 104% | -0.0575em | rgb(93,72,219) purple |
| hero .p paragraph | 5.9028vw (90.96px) | 500 | 6.8056vw | -0.0475em | gradient text (transparent) |
| h2 section titles | 15.2778vw (235px) | 500 | 1:1 | -0.0575em | rgb(0,0,0) |
| program intro | 3.0556vw (47px) | 500 | 118% | -0.0475em | rgba(0,0,0,0.82) |
| list items | 2.4306vw (37px) | 500 | 118% | -0.0475em | rgb(0,0,0) |
| care card text | 2.7083vw (41px) | 500 | 118% | -0.0475em | rgb(255,255,255) |
| FAQ heading | 2.2222vw (34px) | 500 | 125% | normal | rgb(0,0,0) |
| FAQ body | 1.25vw (19px) | 400 | 166% | normal | rgba(0,0,0,0.44) |
| hero bg text | 19.4444vw (299px) | 500 | 1:1 | -0.0575em | gradient |
| footer links | 24px | 400 | 60px | normal | rgb(255,255,255) |

**Key typography patterns:**
- Tight negative letter-spacing everywhere (-0.0475em to -0.0575em)
- Viewport-relative font sizes (vw units) for fluid scaling
- Single weight (500 medium) for almost everything
- Gradient text via `background-clip: text` + `-webkit-text-fill-color: transparent`

---

## 5. Color Palette

### Solid Colors
```
rgb(0, 0, 0)              — primary black, text, backgrounds
rgb(255, 255, 255)        — white, card backgrounds, button bg
rgb(93, 72, 219)          — purple — hero H1 color
rgba(0, 0, 0, 0.82)       — near-black text
rgba(0, 0, 0, 0.44)       — muted text (FAQ body)
rgba(0, 0, 0, 0.06)       — separator bg
rgb(224, 224, 224)        — FAQ border lines
rgb(240, 240, 240)        — intro list text (nearly white)
rgb(248, 186, 252)        — pink/purple (hero radial gradient)
rgba(224, 87, 160, 0.5)   — hot pink (hero radial gradient)
rgba(168, 86, 245, 0.75)  — purple (hero radial gradient)
rgb(53, 47, 51)           — dark brown-black (care-card-1 bg)
rgb(41, 37, 38)           — near-black brown (care-card-1 bg)
rgb(49, 44, 48)           — dark (care-card-2 bg)
```

### Linear Gradients
```css
/* Hero heading text gradient */
linear-gradient(166.14deg, rgb(83, 170, 255) 1.38%, rgb(53, 119, 191) 38.84%, rgb(0, 0, 0) 74.76%)

/* Hero background large text */
linear-gradient(166.14deg, rgb(192, 227, 216) 0px, rgb(186, 225, 220) 100%)   /* "it's all" */
linear-gradient(166.14deg, rgb(232, 244, 247) 0px, rgb(175, 205, 222) 100%)   /* "in" */
linear-gradient(166.14deg, rgb(106, 180, 165) 0px, rgb(134, 183, 212) 100%)   /* "the app" */

/* Program section text */
linear-gradient(123.97deg, rgb(79, 216, 171) 10.62%, rgb(94, 161, 231) 43.12%, rgb(131, 117, 208) 89.61%)

/* Program intro span */
linear-gradient(243.63deg, rgb(63, 209, 148) 16.96%, rgb(47, 165, 158) 60.78%)

/* Care section text */
linear-gradient(93.37deg, rgb(150, 133, 255) -1.4%, rgb(209, 178, 202) 34.29%, rgb(181, 173, 225) 85.34%)

/* Care card-1 background */
linear-gradient(90deg, rgb(53, 47, 51) 0px, rgb(41, 37, 38) 100%)

/* Care card-2 background */
linear-gradient(90deg, rgb(49, 44, 48) 0px, rgb(53, 47, 51) 50%, rgb(41, 37, 38) 100%)

/* Shop section text */
linear-gradient(123.97deg, rgb(127, 191, 188) 10.62%, rgb(85, 107, 113) 49.7%, rgb(0, 0, 0) 89.61%)

/* Shop card content top gradient overlay */
linear-gradient(0deg, rgba(245, 240, 242, 0) 50%, rgba(180, 205, 196, 0.7) 100%)
```

### Radial Gradients (hero background blob)
```css
/* #hero-card-content-gradient::after */
background-image:
  radial-gradient(at 70% 35%, rgba(248, 186, 252, 0.75) 0px, rgba(248, 186, 252, 0) 18%),
  radial-gradient(at 40% 75%, rgba(224, 87, 160, 0.5) 0px, rgba(224, 87, 160, 0) 28%),
  radial-gradient(at 34% 25%, rgba(248, 186, 252, 0.75) 0px, rgba(248, 186, 252, 0) 22%),
  radial-gradient(at 60% 64%, rgba(248, 186, 252, 0.75) 0px, rgba(248, 186, 252, 0) 36%),
  radial-gradient(at 46% 53%, rgba(168, 86, 245, 0.75) 0px, rgba(248, 186, 252, 0) 53%);
background-size: 85% 85%;
background-position: 50% 50%;
background-repeat: no-repeat;
```

---

## 6. Button / CTA Styles

### `.soon` — Primary Download CTA (nav + video section)
```css
tag: a
display: table;
padding: 16px 22px;
border-radius: 52px;
background-color: rgb(255, 255, 255);
box-shadow: rgba(0, 0, 0, 0.06) 0px 8px 30px 0px;
color: rgb(0, 0, 0);
font-family: sofia;
font-size: 14px;
font-weight: 500;
letter-spacing: -0.0175em;
cursor: pointer;

/* Inner structure */
.soon-icon  { float: left; padding-right: 7px; height: 20px; width: 17px; }
.soon-txt   { float: left; margin-top: 2px; height: 20px; line-height: 20px; }

/* Nav position */
#nav .soon { position: absolute; top: 24px; right: 32px; }

/* Video section position */
#video .soon { position: absolute; bottom: 3.33333vw; }
```

No visual hover effects in CSS — hover effects (if any) are JS-driven.

---

## 7. Spacing Pattern

Base horizontal rhythm: **64px side margins** on cards/sections (hard-coded).
Section vertical spacing: **17.3611vw ≈ 267px** at 1541px wide.

| Element | Padding | Margin |
|---------|---------|--------|
| body | 0 | 0 |
| header#hero | top: 100px | 0 |
| .card-shadow | 0 | left/right: 64px |
| div.p (copy blocks) | 11.11vw top, 10.83vw right, 11.11vw left, 17.36vw bottom | 0 |
| #intro | 0 | top: 17.36vw |
| section#program | 0 | top: 17.36vw |
| section#care | 0 | top: 17.36vw + margin-top: 17.36vw |
| section#shop | 0 | top: 17.36vw |
| section#faq | top: 6.94vw | left/right: 64px, bottom: 10.42vw |
| footer | right/left/bottom: 64px | top: 100px |
| #care-card-0 | top: 16.67vw | left/right: 64px, top: 13.89vw |
| #care-card-1, #care-card-2 | 0 | left/right: 64px, top: 32px |

---

## 8. Hero Section — Complete Styles

### header#hero
```css
position: relative;
padding-top: 100px;
width: 100vw;
height: ~5548px (scroll-expanded);
background: transparent;
overflow: visible;
```

### h1 — Headline
```css
text: "Total care. Totally different."
position: relative;
z-index: 4;
padding-top: 8.3333vw;
margin-bottom: -12.5vw;
font-family: sofia;
font-size: 5.625vw;
line-height: 104%;
font-weight: 500;
letter-spacing: -0.0575em;
color: rgb(93, 72, 219);
text-align: center;
```

### .p p — Hero body copy
```css
font-size: 5.9028vw;
line-height: 6.8056vw;
letter-spacing: -0.0475em;
background-image: linear-gradient(166.14deg, rgb(83, 170, 255) 1.38%, rgb(53, 119, 191) 38.84%, rgb(0, 0, 0) 74.76%);
background-clip: text;
-webkit-text-fill-color: transparent;
padding: 11.11vw 10.83vw 17.36vw 11.11vw;
```

### #hero-txt — Massive background text
```css
font-size: 19.4444vw;
line-height: 19.4444vw;
letter-spacing: -0.0575em;
overflow: hidden;
padding-top: 15vh;
padding-bottom: 80vh;

/* "it's all" */
margin-left: -1.3889vw;
background: linear-gradient(166.14deg, rgb(192, 227, 216), rgb(186, 225, 220));
background-clip: text; -webkit-text-fill-color: transparent;

/* "in" — right aligned, padding-top: 45vh */
background: linear-gradient(166.14deg, rgb(232, 244, 247), rgb(175, 205, 222));

/* "the app" — centered, padding-top: 45vh */
background: linear-gradient(166.14deg, rgb(106, 180, 165), rgb(134, 183, 212));
```

### #hero-card-content-gradient — Background blob
```css
position: absolute; z-index: -1; top: 0; left: 0;
width: 100%; height: 100%;
background: rgb(255, 255, 255);
opacity: 0.75; /* JS-controlled, will-change: opacity */

/* ::after — radial gradient blobs */
content: "";
position: absolute; top: 50%; left: 50%;
width: 100%; height: 100%;
transform: translate(-50%, -50%);
background-image: /* 5 radial gradients — see color palette section */;
background-size: 85% 85%;
background-position: 50% 50%;
```

### .card-content — Hero card with clip-path animation
```css
background-image: url("/media/hero/01.jpg");
background-size: contain;
background-position: center bottom;
background-repeat: no-repeat;
clip-path: inset(0px 64px round 45px);
will-change: clip-path;
background-color: rgb(255, 255, 255);
```

---

## 9. Navigation Bar

### nav#nav
```css
position: fixed;
top: 0; left: 0;
width: 100%;
height: 0;            /* intentionally zero — doesn't block scroll */
z-index: 4;
background-color: transparent;
backdrop-filter: none;
box-shadow: none;
```

### #nav-logo
```css
position: absolute;
top: 38px; left: 40px;
height: 24px; width: 145px;
/* Two overlapping SVG divs — toggled by JS */
#nav-logo div {
  will-change: opacity;
  transition: opacity 0.2s cubic-bezier(0.215, 0.61, 0.355, 1);
}
/* .fx class = white logo, default = black logo, .hide = both hidden */
```

### Mobile nav overrides (@media max-width: 750px)
```css
#nav-logo { top: 26px; left: 6.15385vw; height: 18px; width: 109px; }
#nav .soon { top: 12px; right: 16px; }
```

---

## 10. Scroll-Triggered System

No data attributes (no data-scroll, data-aos, data-animate, GSAP markers).

### Custom JS RAF Engine
- `window.R` — Raf, Lerp, LerpM, iLerp, Remap, Clamp, Ease utilities
- `window._A` — app state: `{ s: scrollY, needS, engine, isMobile, win: {w, h} }`

### Scroll engine components

| Component | What it does |
|-----------|-------------|
| clip | Animates `.card-content` clip-path — cards reveal from inset as you scroll |
| programPercent | Animated percentage circle in Programs section |
| list | Fade/slide list items in Programs/Shop via lerp on transform + opacity |
| heroGradient | Fades hero gradient blob opacity based on scroll position |
| navColor | Swaps nav logo black↔white based on current background color |
| shim | Controls vw-based vs vh-based sizing (`html.shim-not-null` vs `html.shim-null`) |

### Key scroll behaviors
1. **Card clip-path reveal** — `.card-content { will-change: clip-path }` animates from `inset(0px 64px round 45px)` to fully open
2. **Hero gradient fade** — opacity controlled by scroll position
3. **Nav logo color swap** — `.fx` class toggles black/white logo
4. **Sticky phone mockup** — `.card-content-phone-sticky { position: sticky; top: 0; }`
5. **List item stagger** — `.card-content-list-sticky-copy { will-change: transform, opacity }` — items fade/slide in via lerp

---

## Design Summary — What Makes This Premium

1. **No CSS animations or keyframes** — everything is RAF-driven JS scroll animation (buttery smooth lerp)
2. **Clip-path reveal** is the signature interaction — cards open from rounded inset as you scroll
3. **Massive typography** — section headings at 15vw, hero body at 5.9vw, bg text at 19.4vw
4. **Gradient text everywhere** — hero heading, hero body, section labels, all use `background-clip: text`
5. **Single font, single weight** — Sofia Pro 500 for everything (400 only for small text)
6. **Tight letter-spacing** — -0.0475em to -0.0575em on all headings
7. **White base with color zones** — sections shift between white bg and dark bg (care section)
8. **Floating nav** — zero-height fixed nav, fully transparent, just logo + pill CTA
9. **Generous vertical spacing** — 17.36vw (~267px) between sections
10. **vw-based sizing** — everything scales with viewport, no breakpoint jumps
