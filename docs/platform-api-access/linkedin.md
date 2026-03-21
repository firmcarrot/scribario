# LinkedIn API Access

## Overview

LinkedIn has a two-tier system (Development and Standard). Personal profile posting is self-serve. Company page posting requires formal application to the Community Management API.

## What We Need

| Scope | Purpose | How to Get |
|---|---|---|
| `w_member_social` | Post to user's personal profile | Self-serve ("Share on LinkedIn" product) |
| `w_organization_social` | Post to company pages | Community Management API (application required) |
| `r_organization_social` | Read org posts/engagement | Community Management API |
| `r_basicprofile` | Access member name and photo | Community Management API |

## Step 1: Self-Serve — Personal Profile Posting

1. Go to linkedin.com/developers
2. Create an app (requires a real LinkedIn Page to associate it with)
3. Under Products tab, add **"Share on LinkedIn"**
4. This immediately grants `w_member_social` — no review needed
5. Implement 3-legged OAuth 2.0 requesting `w_member_social` scope
6. Post via: `POST https://api.linkedin.com/rest/posts`
7. Required headers: `Linkedin-Version: {YYYYMM}`, `X-Restli-Protocol-Version: 2.0.0`

## Step 2: Community Management API — Company Page Posting

### Prerequisites

- Registered legal organization (not individual developer)
- Verified business email (personal Gmail rejected)
- LinkedIn Page verified by a super admin
- Real, functional product demonstrating the use case
- Privacy policy URL on your website
- App name must NOT contain "LinkedIn," "Linked," "In," or Microsoft branding

### Development Tier Application

1. Developer Portal > app > Products tab > Community Management API > access request form
2. Provide: business email, legal org name, registered address, website URL, privacy policy URL
3. LinkedIn verifies: email, organization, website domain, Page verification
4. If approved: 500 API calls/app/day, 100 calls/member/day
5. Timeline: 1-4 weeks (manual review)

### Standard Tier Application

After building/testing in Development tier:

1. My Apps > Products > Standard tier access request form
2. Provide: company overview, product description, use case, test credentials
3. Submit screencast demonstrating your app
4. Timeline: 2-6 weeks after Development tier

## Screencast Requirements (Standard Tier)

For Page Management use case, must show:
- Full OAuth flow: user approving access to their LinkedIn page data
- User posting to their LinkedIn page through your app
- How a comment from a member is displayed in your app
- What personal data from commenter's profile is shown
- Any other functionality using member personal data

Technical requirements:
- High resolution, downloadable (Google Drive or similar)
- Only show screens related to your app
- Narration recommended
- Demonstrate each use case from access request form

## API Versioning

All API calls require `Linkedin-Version: YYYYMM` header. New versions release monthly. Always use a recent version.

## Common Rejection Reasons

- Personal email address used in application
- App name contains LinkedIn branding
- LinkedIn Page not verified by a super admin
- Use case not in supported categories (only commercial B2B tools — no scraping, personal tools, entertainment)
- No real legal organization behind the app

## Cost

Free — no paid tiers for Community Management API.

## Compliance Checklist (Updated March 21, 2026)

| Requirement | Status | Details |
|---|---|---|
| Privacy Policy references LinkedIn data usage | ✅ | Privacy Policy Section 4 |
| LinkedIn Marketing API Terms referenced in ToS | ✅ | ToS Section 4 |
| Per-platform revocation instructions | ✅ | Privacy Policy Section 8 |
| Data retention policy documented | ✅ | Privacy Policy Section 5 |
| privacy@scribario.com email | ⬜ | Ron setting up forwarding |
| LinkedIn Page created for Scribario | ⬜ | Needed to associate app |
| Developer app created | ⬜ | Not started |
| "Share on LinkedIn" product added | ⬜ | Blocked on app creation |
| Community Management API applied | ⬜ | Requires legal org (LLC) |
