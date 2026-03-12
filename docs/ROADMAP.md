# Scribario — Product Roadmap

This roadmap reflects where Scribario is today, what's actively in development, and where the product is heading.

---

## Phase 1 — Core Pipeline ✅ Complete

*Shipped March 2026*

The foundation: a working end-to-end system that takes a text message and publishes a social post.

- [x] Multi-tenant database architecture (14 tables, 7 enums, RLS on all)
- [x] Telegram bot live (`@ScribarioBot`) with aiogram 3.x
- [x] Claude API caption generation — 3 unique options per request, brand-tuned
- [x] Kie.ai Nano Banana 2 image generation — parallel generation (~25s for 3 images)
- [x] Brand voice system — per-tenant brand profiles with few-shot examples
- [x] Per-option approval flow (Approve #1/#2/#3, Reject All, Regenerate)
- [x] Facebook + Instagram publishing via self-hosted Postiz
- [x] pgmq job queue (content_generation + posting queues)
- [x] Background worker with systemd deployment on VPS
- [x] Reference photo support — users can send a photo as image direction
- [x] Brand profile onboarding dialog (aiogram-dialog state machine)
- [x] 147 passing tests, full mypy --strict type checking
- [x] Redis FSM storage — bot state survives restarts

**First live client:** Mondo Shrimp (beta) — posting to Facebook and Instagram

---

## Phase 2 — Growth Features ✅ Complete

*Shipped March 2026*

Making Scribario useful enough that clients don't want to churn.

- [x] **Scheduled posting** — "Post this Saturday at 10am" — dateparser + job_queue.scheduled_for
- [x] **Style system** — per-post style override + per-brand default (photorealistic/cinematic/cartoon/watercolor)
- [x] **Post history** — `/history` shows last 10 posted pieces with platforms + caption preview
- [x] **Caption editing** — ✏️ Edit button per option, FSM flow, re-preview before approving
- [x] **Image regeneration only** — 🖼️ New Image button per option, regenerates image only, keeps caption
- [x] **Usage tracking** — per-tenant cost logging to usage_events (anthropic + kie_ai, per request)
- [x] **Brand voice learning** — approved posts auto-added as few_shot_examples; dedup + 20-example cap
- [x] **Posting confirmation** — Telegram message after every post with actual platform names
- [x] **Multi-platform targeting** — "post to LinkedIn only" narrows which platforms receive the post
- [x] **226 tests**, Redis FSM storage, full type checking

Still in Phase 2 (needs external API access or infrastructure):
- [ ] **Bluesky integration** — AT Protocol OAuth — no review required, pending implementation
- [ ] **LinkedIn personal posting** — no review required, pending implementation
- [ ] **Multi-user tenants** — add team members to a Scribario account
- [ ] **Webhook-based worker** — replace polling with pgmq NOTIFY for lower latency

---

## Phase 3 — Intelligence Layer 📋 Planned

*Target: Q3-Q4 2026*

Making Scribario smarter the longer you use it.

- [x] **Brand voice learning** — automatically improve brand profiles from approved content *(shipped Phase 2)*
- [ ] **Performance feedback loop** — connect analytics data to influence future generation
- [ ] **Composition awareness** — Nano Banana composition guidance for consistent visual identity
- [ ] **Content calendar** — suggest when to post based on historical engagement patterns
- [ ] **A/B testing** — post two variants, track which performs better
- [ ] **Instagram Stories and Reels** — short-form video and story formats
- [ ] **TikTok integration** — requires platform audit (4-12 week process)
- [ ] **Analytics dashboard** — web-based view of post performance across platforms
- [ ] **Competitor insights** — monitor what's working in your category
- [ ] **Hashtag intelligence** — dynamic hashtag selection based on trending data

---

## Phase 4 — Platform Scale 💡 Future

*2027 and beyond*

Turning Scribario from a tool into a platform.

- [ ] **Agency dashboard** — manage multiple clients from one web interface
- [ ] **White-label** — rebrandable Scribario deployments for agencies
- [ ] **API-first mode** — headless Scribario for teams with custom workflows
- [ ] **Mobile app** — native iOS/Android app as an alternative to Telegram
- [ ] **Content templates** — pre-built content series (product spotlight, testimonial, holiday, etc.)
- [ ] **Approval workflows** — multi-step review (creator → manager → client) before posting
- [ ] **CRM integration** — trigger posts from customer milestones, order events, etc.
- [ ] **YouTube / Google** — long-form video support
- [ ] **LinkedIn company pages** — requires Marketing Developer Program membership
- [ ] **X / Twitter** — after revenue supports $200/mo API cost

---

## Platform Integration Status

| Platform | Status | Notes |
|---|---|---|
| Facebook | ✅ Live | Posting via Postiz + Meta Graph API |
| Instagram | ✅ Live | Posting via Postiz + Meta Graph API |
| Bluesky | 📋 Planned Phase 2 | AT Protocol — no review required |
| LinkedIn (personal) | 📋 Planned Phase 2 | No review required |
| YouTube | 📋 Planned Phase 3 | OAuth consent review, 1-4 weeks |
| Pinterest | 📋 Planned Phase 3 | Standard access review, 2-8 weeks |
| TikTok | 📋 Planned Phase 3 | Requires audit, 4-12 weeks |
| LinkedIn (company) | 💡 Future | Requires Marketing Developer Program |
| X / Twitter | 💡 Future | $200/mo API minimum cost |

---

## For Investors

Scribario is solving a real, recurring pain: small and medium businesses know they need consistent social media presence, but don't have the time, skills, or budget for a content team. Current solutions (hiring an agency, using Canva + ChatGPT manually, buying scheduling tools) are either expensive, time-consuming, or produce generic content.

**What makes Scribario different:**

1. **Zero friction interface** — Telegram means no new app to learn, no login to remember
2. **Brand voice that improves over time** — the AI learns your voice from your approved content
3. **End-to-end** — idea to published post in one conversation, no tool switching
4. **Multi-tenant and white-labelable** — built to be sold through agencies at scale

**Current traction:**
- First beta client live, posting to Facebook + Instagram
- End-to-end working: message → preview → approve → live post in under 45 seconds
- 226 automated tests, production-grade architecture from day one

**Revenue model:**
- SaaS subscription tiers (Starter / Growth / Pro) based on post volume
- Agency tier with white-label and multi-client management
- AI API costs are bundled into subscription pricing — no BYOK, no complexity for clients
