# Scribario Brand Guide

## Identity

**Name:** Scribario
**Tagline:** "Your social media team in a text."
**CTA:** "Try it free → @ScribarioBot"
**Alternate tagline:** "Text it. We post it."

## Logo

The Scribario logo is a **single fluid pen-stroke S** — calligraphic, slightly imperfect, human. It should look like a confident signature written in one motion.

**Primary mark:** White S on coral-orange background
**Secondary mark:** Coral-orange S on transparent/white background

### Logo files

| File | Use |
|---|---|
| `logo-white-on-orange-2048.png` | Primary logo, any size |
| `logo-white-on-orange-320.png` | Facebook/social profile pics |
| `logo-orange-on-transparent-2048.png` | Dark backgrounds, overlays |
| `logo-original-calligraphy.png` | Original brush-stroke master |

### Logo rules
- Never stretch or distort the S
- Minimum clear space: 25% of logo width on all sides
- Never place the orange logo on similarly warm backgrounds
- The S must always be the **exact same stroke** — do not regenerate or redraw

## Colors

### Primary

| Name | Hex | RGB | Use |
|---|---|---|---|
| **Coral Orange** | `#FF6B4A` | 255, 107, 74 | Logo background, CTAs, accents |
| **Deep Navy** | `#1A1A2E` | 26, 26, 46 | Backgrounds, headers |
| **Near Black** | `#0F0F23` | 15, 15, 35 | Dark gradient endpoint |
| **White** | `#FFFFFF` | 255, 255, 255 | Text on dark, logo mark |

### Supporting

| Name | Hex | RGB | Use |
|---|---|---|---|
| **Muted Gray** | `#8E8E9A` | 142, 142, 154 | Secondary text, subtitles |
| **Light Gray** | `#F5F5F7` | 245, 245, 247 | Light backgrounds |
| **Telegram Blue** | `#0088CC` | 0, 136, 204 | Chat bubbles, Telegram references |

## Typography

### Primary font: Sans-serif, clean, modern
**Recommended:** Inter, SF Pro Display, or similar geometric sans-serif
- Headlines: Semi-Bold or Bold, tracking -0.02em
- Body: Regular, tracking 0
- Avoid script/serif fonts for body text — the logo provides the handwritten element

### Hierarchy

| Element | Weight | Size (relative) |
|---|---|---|
| Hero headline | Bold | 48-64px |
| Section title | Semi-Bold | 24-32px |
| Body text | Regular | 16-18px |
| Caption/meta | Regular | 12-14px |
| CTA button | Bold | 16-18px |

## Voice & Tone

- **Confident, not cocky** — we know what we do well
- **Direct, not corporate** — talk like a person, not a press release
- **Effortless, not lazy** — the product is easy, the quality is high
- **Never say:** "AI-powered" in customer-facing copy (it's implied)
- **Always say:** what the user gets, not how the tech works

### Examples

| Do | Don't |
|---|---|
| "Your social media team in a text." | "AI-powered social media automation platform." |
| "Send a message. Get a post." | "Leverage machine learning for content optimization." |
| "Try it free." | "Sign up for our freemium tier." |

## Social Media Dimensions

### Facebook

| Asset | Size | File |
|---|---|---|
| Profile picture | 320x320 (displays 170x170) | `logo-white-on-orange-320.png` |
| Cover/banner | Upload full-size, FB crops to 820x312 desktop / 640x360 mobile | `fb-banner-fullsize.png` |

**Banner safe zone:** Keep text and critical elements in center 640x312px. Left 200px is covered by profile picture on desktop.

### Instagram

| Asset | Size |
|---|---|
| Profile picture | 320x320 |
| Feed post | 1080x1080 (1:1) |
| Story | 1080x1920 (9:16) |

### General

| Asset | Aspect ratio |
|---|---|
| Social post square | 1:1 |
| Landscape post | 16:9 |
| Story/reel | 9:16 |
| Banner/hero | 21:9 |

## Image Generation (Nano Banana 2)

When generating branded images with Kie.ai Nano Banana 2:

- **Always include** the logo or S mark as a reference image for brand consistency
- **Default style:** photorealistic unless otherwise specified
- **Identity lock prompt** (when using reference photos of people): "Maintain the exact same facial features as the reference images — identical eye shape, nose bridge contour, jawline angle, lip proportions, and skin texture. Do not change the face."
- **Sweet spot:** 4-6 reference images for face consistency
- **Aspect ratios:** Use `21:9` for banners, `1:1` for social posts, `9:16` for stories

## Brand Assets Location

All master files: `/home/ronald/projects/scribario/brand/`
