# Scribario — Social Media Integrations

All credentials also live in `.env` on dev and `/opt/scribario/.env` on VPS.

---

## Infrastructure

| Service | URL | Notes |
|---|---|---|
| Postiz | https://postiz.scribario.com | Self-hosted Docker on VPS |
| Postiz Admin Login | ron@scribario.com / Scribario2026x | Admin account |
| Postiz Org ID | `06f9862f-ea5f-4b95-a4cd-c8ad9cc2f73a` | Scribario org |
| Postiz API Key | `87f3585eb2cb7ebf216485407aac16d4cd33689951fe99cdec361575770380f8` | In .env as POSTIZ_API_KEY |
| VPS | 31.97.13.213 (Hostinger) | SSH: `ssh -i ~/.ssh/id_hostinger root@31.97.13.213` |

---

## Meta (Facebook + Instagram + Threads)

**Status:** App created, credentials in Postiz, OAuth redirect registered. NOT yet published — in development mode only.

| Field | Value |
|---|---|
| Meta App Name | Scribario |
| App ID | `1580831456516304` |
| App Secret | `1abadec628b059e6e92f607399d111ae` |
| Facebook Page | Scribario (created 2026-03-11) |
| Developer Account | ronald.nadelberg@gmail.com |
| App Status | Development (unpublished) |
| Use Cases | Manage everything on your Page, Manage messaging & content on Instagram |
| OAuth Redirect URI | `https://postiz.scribario.com/integrations/social/facebook` |
| Business Portfolio | None connected yet |

**To go live:** Need App Review submission with screen recording demo + privacy policy URL.

**Compliance (done in v1.1):**
- Data Deletion Callback endpoint: `POST /api/meta-data-deletion` (HMAC-SHA256 signed_request verification)
- Deletion status page: `GET /data-deletion-status?code=XXX`
- Privacy Policy references Meta deletion callback flow
- Per-platform revocation instructions in Privacy Policy Section 8
- `FACEBOOK_APP_SECRET` env var must be set on Vercel for callback verification

**In .env:**
```
FACEBOOK_APP_ID=1580831456516304
FACEBOOK_APP_SECRET=1abadec628b059e6e92f607399d111ae
```

---

## Instagram

Shares the same Meta app as Facebook (same App ID/Secret).
OAuth redirect: `https://postiz.scribario.com/integrations/social/instagram`

---

## Threads

Shares the same Meta app as Facebook.
OAuth redirect: `https://postiz.scribario.com/integrations/social/threads`

---

## TikTok

**Status:** NOT SET UP

Requires: TikTok Developer account + app review + separate audit for public posting.
Estimated time: 4-12 weeks after submission.

---

## LinkedIn

**Status:** NOT SET UP

Personal posting: No review needed.
Company page posting: Requires Marketing Developer Program + legal business entity.

---

## YouTube / Google

**Status:** NOT SET UP

Requires: Google Cloud project + YouTube Data API v3 + OAuth consent screen verification (1-4 weeks).
Default quota: 10,000 units/day (~6 video uploads). Need quota extension for real usage.

---

## X / Twitter

**Status:** NOT SET UP

Cost: $200/month minimum (Basic tier, 10K posts/month).
Recommendation: Add as paid premium add-on after initial launch.

---

## Pinterest

**Status:** NOT SET UP

Requires: Standard access review (2-8 weeks, opaque process).

---

## Bluesky

**Status:** NOT SET UP

No app review, no cost, fully open. Easiest platform to add.
Uses AT Protocol OAuth — publish `client_metadata.json` at a public URL.

---

## Legal & Compliance (v1.1 — March 21, 2026)

All platform compliance requirements have been addressed in Privacy Policy v1.1 and Terms of Service v1.1:

| Requirement | Status | Notes |
|---|---|---|
| Meta Data Deletion Callback | ✅ Built | `POST /api/meta-data-deletion` with HMAC-SHA256 |
| Deletion Status Page | ✅ Built | `GET /data-deletion-status?code=XXX` |
| YouTube/Google API disclosure | ✅ Added | Privacy Policy references Google Privacy Policy + YouTube ToS |
| Google API User Data Policy | ✅ Added | Limited Use compliance statement in Privacy Policy |
| Per-platform revocation instructions | ✅ Added | Privacy Policy Section 8 |
| TikTok AITGC labeling | ✅ Added | ToS Section 6c |
| X Automation Rules reference | ✅ Added | ToS Section 4 |
| LinkedIn Marketing API Terms | ✅ Added | ToS Section 4 |
| Cookie section | ✅ Fixed | Essential only, no tracking (honest) |
| privacy@scribario.com | ⬜ Pending | Ron setting up Namecheap email forwarding |
| FACEBOOK_APP_SECRET on Vercel | ⬜ Pending | Needed for deletion callback verification |

## Setup Priority

1. ✅ Facebook + Instagram + Threads (one Meta app — DONE, needs App Review to go public)
2. ⬜ Bluesky (zero friction, build next)
3. ⬜ LinkedIn personal (no review needed)
4. ⬜ YouTube (OAuth consent screen, 1-4 weeks)
5. ⬜ Pinterest (Standard access, 2-8 weeks)
6. ⬜ X/Twitter (after revenue, $200/mo)
7. ⬜ TikTok (after other platforms, 4-12 week audit)
8. ⬜ LinkedIn company pages (after incorporation)
