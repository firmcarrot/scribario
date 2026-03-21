# X (Twitter) API Access

## Overview

X uses a consumption-based billing model (credits). No fixed monthly subscription — pay per API request. Developer account approval is the main gate.

## Current Billing Model

- Credit-based, pay only for what you use
- Purchase credits upfront, deducted per API request
- Different endpoints have different per-call costs (visible in Developer Console)
- Monthly cap: 2 million Post reads on standard plans
- 24-hour deduplication: same resource requested twice = one charge
- **Free tier** exists for testing (limited read access; write requires credits)
- **Enterprise plan** available for high-volume (custom rates, full firehose)

## What We Need

**OAuth 2.0 with PKCE** (current standard):

| Scope | Purpose |
|---|---|
| `tweet.write` | Create and delete tweets |
| `users.read` | Read user account info (required dependency) |
| `offline.access` | Get refresh tokens for persistent access |

`offline.access` is critical — without it, tokens expire after 2 hours.

## Step 1: Developer Account

1. Apply at developer.x.com
2. Describe what you're building, what data you access, how you'll use it (be specific)
3. Create a Project and App in the Developer Console
4. Set redirect URI in app settings
5. Enable "OAuth 2.0" in app settings

## Step 2: OAuth 2.0 PKCE Flow

1. **Generate PKCE parameters**: `code_verifier` (random 43-128 chars) + `code_challenge` (SHA-256 hash, base64url-encoded)
2. **Authorization URL**:
   ```
   https://x.com/i/oauth2/authorize
   ?response_type=code
   &client_id={your_client_id}
   &redirect_uri={your_redirect_uri}
   &scope=tweet.write%20users.read%20offline.access
   &state={random_state}
   &code_challenge={code_challenge}
   &code_challenge_method=S256
   ```
3. **Redirect user** to that URL
4. **Receive authorization code** — valid only 30 seconds, handle immediately
5. **Exchange for tokens**: POST to `https://api.x.com/2/oauth2/token` with `grant_type=authorization_code`, code, `code_verifier`, `redirect_uri`
6. **Store access + refresh tokens**
7. **Refresh** via same endpoint with `grant_type=refresh_token`

## Step 3: Posting

Endpoint: `POST https://api.x.com/2/tweets`
Header: `Authorization: Bearer {USER_ACCESS_TOKEN}`

Must be the user's OAuth token (not your app-level Bearer token). Each user goes through OAuth independently.

## Common Issues

- Developer account rejected if use case description is vague
- Apps flagged for automated/bulk posting may be restricted
- X enforces Automation Rules — bulk posting tools must include human oversight
- Inauthentic engagement = permanent suspension

## Cost

Credits-based — check console.x.com for current per-endpoint pricing. No public fixed pricing page.

## Timeline

Account approval: days. API access: instant after credits purchased.

## Compliance Checklist (Updated March 21, 2026)

| Requirement | Status | Details |
|---|---|---|
| Privacy Policy references X/Twitter data usage | ✅ | Privacy Policy Section 4 |
| X Automation Rules referenced in ToS | ✅ | ToS Section 4 |
| Per-platform revocation instructions | ✅ | Privacy Policy Section 8 |
| Data retention policy documented | ✅ | Privacy Policy Section 5 |
| Anti-surveillance clause | ✅ | ToS Section 4 |
| privacy@scribario.com email | ⬜ | Ron setting up forwarding |
| Developer account applied | ⬜ | Not started — deferred until revenue |
| Credits purchased | ⬜ | Deferred — cost-gated |
