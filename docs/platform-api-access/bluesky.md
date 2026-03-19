# Bluesky (AT Protocol) API Access

## Overview

Bluesky is built on the **AT Protocol** — open, federated. No app review, no business verification, no partner program. Two auth options: App Passwords (simple, for bots) or OAuth 2.0 (for multi-user apps).

## Option A: App Passwords (Recommended for Server-Side)

App passwords are single-purpose credentials:
- Separate from user's main password
- Individually revokable
- Scoped — can't change email/password
- Created by user in Bluesky settings

### How to Use

1. User: Bluesky Settings > Privacy and Security > App Passwords
2. User creates app password named "Scribario"
3. User provides password to your app
4. Your app calls:
   ```
   POST https://bsky.social/xrpc/com.atproto.server.createSession
   {"identifier": "user.handle", "password": "app-password"}
   ```
5. Response: `accessJwt` (short-lived) + `refreshJwt` (long-lived)
6. Use `accessJwt` as Bearer token for all calls
7. Refresh via `com.atproto.server.refreshSession`

### Posting

```
POST https://bsky.social/xrpc/com.atproto.repo.createRecord
Authorization: Bearer {accessJwt}
{
  "repo": "{user_did}",
  "collection": "app.bsky.feed.post",
  "record": {
    "$type": "app.bsky.feed.post",
    "text": "your post content",
    "createdAt": "{ISO timestamp}"
  }
}
```

## Option B: OAuth 2.0 (For Multi-User Apps)

AT Protocol implements OAuth 2.1:

- No pre-registration — clients identified by `client_id` URL pointing to a Client Metadata Document you host
- Metadata document served at HTTPS URL
- Works across different Bluesky-compatible servers (not just bsky.social)
- Uses **DPoP** (Demonstrating Proof-of-Possession) headers — non-standard, requires library support

**Required scope:** `atproto` (mandatory). Additional: `transition:generic` as needed.

**Implementation:**
- Use `@atproto/oauth-client` (TypeScript) or `atproto` (Python)
- Do NOT implement DPoP from scratch
- `client_id` is your metadata URL, not a string identifier
- No pre-approval or review — any valid client metadata is accepted

**Note:** OAuth not recommended for headless clients (bots, scheduled posting). Use App Passwords for those.

## No Review Process

No app review. No business verification. No partner program. Anyone can post via AT Protocol.

Only restrictions: rate limits and Community Guidelines.

## Rate Limits

- Global: ~3,000 requests per 5 minutes per IP
- Account-level: ~100 creates/hour per account (approximate, subject to change)

## SDKs

- TypeScript: `@atproto/api` (official)
- Python: `atproto` (community, widely used)

## Cost

Completely free. No tiers, no fees.

## Scribario-Specific Notes

- App Passwords approach is simplest for our bot-based architecture
- User provides app password during onboarding, we store encrypted in Supabase Vault
- Can ship Bluesky support immediately — no review wait
