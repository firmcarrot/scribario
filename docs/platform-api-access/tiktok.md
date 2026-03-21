# TikTok Content Posting API Access

## Overview

TikTok uses the **Content Posting API** with two phases: sandbox (all posts forced to private) and production (public posting after audit).

## Prerequisites

- TikTok for Developers account at developers.tiktok.com
- Real, functional app with website, privacy policy, and terms of service
- App must be published (not development phase) before audit submission
- For mobile apps: must be on App Store or Google Play

## Step 1: Register and Configure

1. Go to developers.tiktok.com, create developer account
2. Create new app: My Apps > Create App
3. Under Products tab, add **Content Posting API**
4. Enable **Direct Post** in app configuration
5. App starts in sandbox mode

## Required Scope

**`video.publish`** — the single scope needed for video posting. Must be authorized by each user via OAuth.

## Step 2: Sandbox Testing

While unaudited:
- All posts forced to **private** regardless of visibility settings
- Error `unaudited_client_can_only_post_to_private_accounts` if trying public
- Test the full flow: OAuth, upload, post, status checking
- Use real TikTok accounts — no fake "test accounts"

## Content Format Requirements

**Videos:**
- Format: MP4 with H.264 encoding
- Upload methods: `FILE_UPLOAD` (direct chunked) or `PULL_FROM_URL` (TikTok fetches — domain must be pre-verified)
- Upload URLs expire after 1 hour

**Photos:**
- Only `PULL_FROM_URL` method (no file upload for photos)
- Domain must be pre-verified with TikTok

## Step 3: Production Audit

This removes the private-only restriction:

1. Build integration fully, test in sandbox
2. Submit **App Review** via Developer Portal
3. Required for submission:
   - Detailed explanation of how `video.publish` enhances user experience
   - Up to 5 demo videos (max 50 MB each) showing complete end-to-end flow
   - For web: domain in demo must match registered website URL
4. TikTok reviews for compliance with ToS and Developer Guidelines
5. If approved, private-only restriction lifted

## App Review Requirements

**App name:**
- Must match your app/website name
- Cannot contain "TikTok" or reference other social media platforms

**Description:**
- What your app does and how it uses each scope
- Must not describe an app still in development or for private/internal use

**Website:**
- Real, functioning website (not placeholder)
- Privacy Policy and Terms of Service publicly visible

## Common Rejection Reasons

- App website is placeholder or under construction
- Demo video doesn't show complete OAuth flow
- App name includes "TikTok"
- Use case appears to be scraping or inauthentic engagement
- Privacy policy not accessible on website

## Rate Limits

6 requests per minute per user access token for Direct Post endpoint.

## Timeline

1-4 weeks (not officially published). Incomplete submissions rejected without feedback.

## Cost

Free — no paid tier for Content Posting API.

## Compliance Checklist (Updated March 21, 2026)

| Requirement | Status | Details |
|---|---|---|
| Privacy Policy references TikTok data usage | ✅ | Privacy Policy Section 4 |
| TikTok Developer Terms compliance | ✅ | ToS Section 4 |
| AITGC labeling for AI-generated content | ✅ | ToS Section 6c — TikTok requires `is_aigc=true` flag |
| Per-platform revocation instructions | ✅ | Privacy Policy Section 8 |
| Data retention policy documented | ✅ | Privacy Policy Section 5 |
| privacy@scribario.com email | ⬜ | Ron setting up forwarding |
| App created on developers.tiktok.com | ⬜ | Not started |
| Sandbox testing complete | ⬜ | Blocked on app creation |
| Production audit submitted | ⬜ | Blocked on sandbox testing |
