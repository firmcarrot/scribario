# Scribario — Cost Analysis & Pricing Reference

**Last updated:** 2026-03-13
**Purpose:** Ground truth for all API costs, infrastructure costs, and pricing decisions.
**Verification status:** Claude API and Kie.ai prices verified against live source pages 2026-03-13. ElevenLabs, Supabase, Hostinger prices from training data (pages didn't render for live verification).

---

## Fixed Costs (Monthly, Regardless of Volume)

| Item | Cost/mo | Notes | Source | Verified |
|---|---|---|---|---|
| Hostinger VPS (KVM 1-2) | $6-13 | Runs bot + worker + Postiz + Redis. IP: 31.97.13.213 | [hostinger.com/pricing/vps-hosting](https://www.hostinger.com/pricing/vps-hosting) | Training data |
| Supabase (Pro plan) | $25 | 8GB DB, 100GB storage, 2M edge fn calls. $10 compute credit included | [supabase.com/pricing](https://supabase.com/pricing) | Training data |
| ElevenLabs (Creator plan) | $11 | 100K chars/mo for TTS + SFX API access | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) | Training data |
| Postiz (self-hosted) | $0 | Apache-licensed open source, full feature parity | [postiz.com/pricing](https://postiz.com/pricing) | N/A |
| Redis (self-hosted) | $0 | AGPLv3 as of Redis 8 (2025), free to self-host | [redis.io/open-source](https://redis.io/open-source/) | N/A |
| Telegram Bot API | $0 | Free, no per-message cost | [core.telegram.org/bots/api](https://core.telegram.org/bots/api) | N/A |
| **Total fixed** | **~$42-49/mo** | | |

---

## Variable Costs (Per API Call)

### Anthropic Claude API (VERIFIED 2026-03-13)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Source |
|---|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 | [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Sonnet 4.6 | $3.00 | $15.00 | Same |

**Discounts:** Prompt caching: cache hits = 0.1x base input (90% off). Batch API: 50% off all prices.

**Per-call estimates (Scribario context):**
- Intake Agent (Haiku, ~500 input + ~200 output tokens): **~$0.0015/call**
- Prompt Engine (Sonnet, ~2000 input + ~1500 output tokens): **~$0.03-0.04/call**
- Caption revision (Sonnet, ~1500 input + ~800 output tokens): **~$0.02/call**

*Note: Token count estimates are based on our prompt sizes. Actual usage may vary 20-30%.*

### Kie.ai — Image & Video Generation (VERIFIED 2026-03-13)

| Product | Credits | Dollar Cost | Source |
|---|---|---|---|
| Nano Banana 2 (1K resolution) | 8 credits | **$0.04/image** | [kie.ai/nano-banana-2](https://kie.ai/nano-banana-2) |
| Nano Banana 2 (2K resolution) | 12 credits | **$0.06/image** | Same |
| Nano Banana 2 (4K resolution) | 18 credits | **$0.09/image** | Same |
| Veo 3 Fast (8s video with audio) | 80 credits | **$0.40/clip** | [kie.ai/v3-api-pricing](https://kie.ai/v3-api-pricing) |
| Veo 3 Quality (8s video with audio) | 400 credits | **$2.00/clip** | Same |

**Credit rate:** $0.005 per credit. No subscription required — pay-as-you-go credit top-ups, minimum $5.

**Note:** High-tier top-ups include a 10% credit bonus, dropping effective per-credit cost to ~$0.0045.

### Google Veo 3.1 (Direct API — more expensive than Kie.ai) (VERIFIED 2026-03-13)

| Model | Cost per second | 8-second clip | Source |
|---|---|---|---|
| Veo 3.1 Standard (720p/1080p) | $0.40/sec | **$3.20/clip** | [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| Veo 3.1 Standard (4K) | $0.60/sec | **$4.80/clip** | Same |
| Veo 3.1 Fast (720p/1080p) | $0.15/sec | **$1.20/clip** | Same |
| Veo 3.1 Fast (4K) | $0.35/sec | **$2.80/clip** | Same |

**Recommendation:** Always use Veo via Kie.ai ($0.40/clip) instead of direct Google API ($1.20-3.20/clip). Saves 67-88%.

### ElevenLabs — TTS & Sound Effects (training data — not live-verified)

| Product | Cost | Unit | Source |
|---|---|---|---|
| TTS (Creator plan) | $0.11/1K chars | Per 1,000 characters | [elevenlabs.io/pricing/api](https://elevenlabs.io/pricing/api) |
| TTS (Pro plan) | $0.18/1K chars at overage | Over 500K chars/mo | Same |
| Sound Effects (auto-duration) | 200 credits = ~$0.022 | Per generation | [help.elevenlabs.io](https://help.elevenlabs.io/hc/en-us/articles/25735337678481-How-much-does-it-cost-to-generate-sound-effects) |
| Sound Effects (fixed duration) | 40 credits/sec | Per second of output | Same |

**Credit-to-dollar conversion (Creator plan):** 100,000 credits / $11 = $0.000110/credit

**Per-scene TTS estimate:** ~150 chars/scene voiceover = ~$0.017/scene

---

## Cost Per Content Type (CORRECTED 2026-03-13)

### Image Post (3 images at 1K + 3 captions)

| Step | Service | Cost |
|---|---|---|
| Intake Agent | Claude Haiku 4.5 | $0.002 |
| Prompt Engine | Claude Sonnet 4.6 | $0.04 |
| 3 images (1K) | Kie.ai Nano Banana 2 | $0.12 |
| **Total** | | **$0.16** |

### Short Video (single 8s clip)

| Step | Service | Cost |
|---|---|---|
| Intake Agent | Claude Haiku 4.5 | $0.002 |
| Prompt Engine | Claude Sonnet 4.6 | $0.04 |
| Start frame (1K) | Kie.ai Nano Banana 2 | $0.04 |
| Video clip | Veo 3 Fast via Kie.ai | $0.40 |
| **Total** | | **$0.48** |

### Long Video (4 scenes, ~30s)

| Step | Service | Cost |
|---|---|---|
| Intake Agent | Claude Haiku 4.5 | $0.002 |
| Prompt Engine | Claude Sonnet 4.6 | $0.04 |
| TTS voiceover (4 scenes) | ElevenLabs | $0.07 |
| Start+end frames (8 images, 1K) | Kie.ai Nano Banana 2 | $0.32 |
| Video clips (4 clips) | Veo 3 Fast via Kie.ai | $1.60 |
| Sound effects (4 scenes) | ElevenLabs | $0.09 |
| FFmpeg stitch | Free | $0.00 |
| **Total** | | **$2.18** |

### Minor Operations

| Operation | Service | Cost |
|---|---|---|
| Caption revision (AI-assisted) | Claude Sonnet 4.6 | ~$0.02 |
| Image-only regen (1 image, 1K) | Kie.ai Nano Banana 2 | $0.04 |
| Brand profile scrape + gen | Claude Sonnet + httpx | ~$0.03 |
| Post from Content Library (as-is) | Postiz only | $0.00 |

---

## Pricing Model (Post-Based — Final)

### Philosophy

Sell **posts**, not credits or tokens. SMB owners think in "I need to post 3 times a week." Credits cause "credit anxiety" — hesitation to use the product. Simple rules:

1. **Generating = 1 post** (counts against monthly limit)
2. **Posting from Content Library as-is = free** (already paid for it)
3. **AI-assisted edits on library items = 1 post** (new AI work)
4. **Manual text edits (user types it) = free**

### Content Library

Every generation gives 3 options. User approves 1. The other 2 can be **saved to Content Library** via a "Save to Library" button. Saved items can be posted later for free (no additional generation cost). AI edits on library items count as a new post.

| Tier | Library Slots |
|---|---|
| Starter | 25 |
| Growth | 100 |
| Pro | Unlimited |

### Three Tiers

| Tier | Price/mo | Image Posts | Short Videos | Long Videos | Platforms | Content Library |
|---|---|---|---|---|---|---|
| **Starter** | $29/mo | 15 | 3 | 0 | 3 platforms | 25 slots |
| **Growth** | $59/mo | 40 | 10 | 2 | 6 platforms | 100 slots |
| **Pro** | $99/mo | 100 | 25 | 5 | 9 platforms (all) | Unlimited |

### Our Cost Per Tier (Worst Case — 100% Utilization)

| Tier | Image Posts | Short Videos | Long Videos | Total COGS | Margin |
|---|---|---|---|---|---|
| **Starter** | 15 x $0.16 = $2.40 | 3 x $0.48 = $1.44 | 0 | **$3.84** | **87%** |
| **Growth** | 40 x $0.16 = $6.40 | 10 x $0.48 = $4.80 | 2 x $2.18 = $4.36 | **$15.56** | **74%** |
| **Pro** | 100 x $0.16 = $16.00 | 25 x $0.48 = $12.00 | 5 x $2.18 = $10.90 | **$38.90** | **61%** |

**Realistic margins (40-60% utilization):** Starter ~93%, Growth ~87%, Pro ~80%

### Add-On Packs

| Add-On | Price | What You Get |
|---|---|---|
| Extra 10 image posts | $5 | For users who hit their limit |
| Extra 5 short videos | $12 | Video-heavy users |
| Extra 1 long video | $6 | One-off video needs |
| Brand voice setup | $29 one-time | White-glove AI brand profile from website scrape + call |

### Annual Discount

20% off for annual billing:
- Starter: $279/yr ($23.25/mo effective)
- Growth: $567/yr ($47.25/mo effective)
- Pro: $948/yr ($79/mo effective)

### 7-Day Free Trial

Full Growth tier features. No credit card required. Converts with "your trial is ending" nudge.

---

## Break-Even Analysis

| Metric | Value |
|---|---|
| Fixed costs | ~$42-49/mo |
| Starter subscribers to cover fixed | 2 users ($58/mo revenue) |
| Growth subscribers to cover fixed | 1 user ($59/mo revenue) |
| Marginal cost of adding one user | $0 (until they generate content) |

---

## Competitive Context

| Alternative | Monthly Cost | What They Get |
|---|---|---|
| Social media manager (hire) | $750-2,000/mo | Human doing the work |
| Agency retainer | $1,500-5,000/mo | Strategy + content + posting |
| Canva Pro + Buffer (DIY) | $50-100/mo | Tools only, user still does the work |
| Alkai.ai | $19-27/mo | Auto-generates + posts, no approval, no real images |
| **Scribario (Growth)** | **$59/mo** | AI generates + you approve + auto-posts. Real images. Video. |

Scribario is not competing on API cost. It's competing on value against hiring a person.

---

## Key Decision: Veo Provider

Using Veo via Kie.ai instead of direct Google API saves:
- Per clip: $0.80 savings ($1.20 vs $0.40)
- Per 4-scene long video: $3.20 savings
- Per 100 long videos/mo: $320 savings

**Always route video generation through Kie.ai unless quality requires Google direct.**

---

## Sources & Citations

1. **Anthropic Claude Pricing:** [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing) — VERIFIED 2026-03-13
2. **Kie.ai Nano Banana 2:** [kie.ai/nano-banana-2](https://kie.ai/nano-banana-2) — VERIFIED 2026-03-13
3. **Kie.ai Veo 3 API Pricing:** [kie.ai/v3-api-pricing](https://kie.ai/v3-api-pricing) — VERIFIED 2026-03-13
4. **Google Gemini/Veo Pricing:** [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing) — VERIFIED 2026-03-13
5. **ElevenLabs Pricing:** [elevenlabs.io/pricing](https://elevenlabs.io/pricing) — training data
6. **ElevenLabs API Pricing:** [elevenlabs.io/pricing/api](https://elevenlabs.io/pricing/api) — training data
7. **ElevenLabs SFX Cost:** [help.elevenlabs.io/hc/en-us/articles/25735337678481](https://help.elevenlabs.io/hc/en-us/articles/25735337678481-How-much-does-it-cost-to-generate-sound-effects) — training data
8. **Kie.ai Pricing:** [kie.ai/pricing](https://kie.ai/pricing) — VERIFIED 2026-03-13
9. **Postiz Pricing:** [postiz.com/pricing](https://postiz.com/pricing) — N/A (free)
10. **Supabase Pricing:** [supabase.com/pricing](https://supabase.com/pricing) — training data
11. **Hostinger VPS Pricing:** [hostinger.com/pricing/vps-hosting](https://www.hostinger.com/pricing/vps-hosting) — training data
12. **Telegram Bot API:** [core.telegram.org/bots/api](https://core.telegram.org/bots/api) — N/A (free)
13. **Redis Licensing:** [redis.io/open-source](https://redis.io/open-source/) — N/A (free)
