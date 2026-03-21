# YouTube Data API v3 Access

## Overview

YouTube uses the YouTube Data API v3 via Google Cloud Console. Video uploading requires the `youtube.upload` scope — a **sensitive scope** that triggers Google's OAuth verification process.

## Prerequisites

- Google account
- Google Cloud Console project at console.cloud.google.com
- Domain ownership verified in Google Search Console
- Publicly accessible homepage with privacy policy on verified domain

## Step 1: Google Cloud Console Setup

1. Go to console.cloud.google.com
2. Create a new project (separate projects for production vs testing)
3. Enable YouTube Data API v3: APIs & Services > Library > search "YouTube Data API v3" > Enable
4. Create credentials: APIs & Services > Credentials > Create Credentials > OAuth Client ID
5. Select application type (Web Application)
6. Add authorized redirect URIs

## Step 2: OAuth Consent Screen

1. APIs & Services > OAuth Consent Screen
2. Select **External** user type
3. Fill in:
   - App name
   - User support email
   - App domain (must be on verified domain)
   - Privacy policy URL (same domain as homepage)
   - Terms of service URL (recommended)
   - Developer contact email
4. Add scope: `https://www.googleapis.com/auth/youtube.upload`
5. Add test users (Google accounts for testing phase)

## Step 3: Testing Phase

While app is in "Testing" status:
- Only explicitly added test users can authorize (up to 100)
- OAuth screen shows "Unverified app" warning
- No time limit on testing phase
- Full functionality available to test users

## Step 4: Brand Verification

Before sensitive scope verification:

1. Verify domain in Google Search Console
2. In OAuth Consent Screen, click "Verify domain" next to app domain
3. Timeline: 2-3 business days
4. Required: app name and logo accurately represent your product

## Step 5: Sensitive Scope Verification (youtube.upload)

1. In OAuth Consent Screen, click "Prepare for verification" / "Submit for verification"
2. Describe how your app uses `youtube.upload` — what users do, why they upload to YouTube, how data is protected
3. Verify all authorized domains
4. Google's OAuth review team evaluates
5. Timeline: 2-4 weeks (can be longer)
6. Once approved: "Unverified app" warning removed, any Google account can authorize

## Step 6: Quota Management

Default quota: **10,000 units/day**. Video upload = 100 units = 100 uploads/day max.

If you need more:
1. Submit **YouTube API Services — Audit and Quota Extension Form**
2. YouTube API team contacts you for compliance audit
3. Audit verifies ToS compliance and legitimate usage
4. If audited within 12 months, use Audited Developer Requests Form for additional quota

## Required Scopes

| Scope | Purpose |
|---|---|
| `youtube.upload` | Upload videos to YouTube |
| `youtube` | Full account access (broader — only if needed) |
| `youtube.readonly` | Read channel/video data |

For posting tool: `youtube.upload` alone is sufficient.

## Common Rejection Reasons

- App description doesn't explain why users need to upload to YouTube
- Privacy policy not accessible or doesn't cover YouTube data usage
- Domain not verified in Google Search Console
- App homepage not publicly accessible
- Requesting broader scopes than use case requires
- Separate production/testing projects not maintained

## Cost

Free but quota-limited. Quota increases free after audit approval.

## Compliance Checklist (Updated March 21, 2026)

| Requirement | Status | Details |
|---|---|---|
| Privacy Policy references Google Privacy Policy | ✅ | Link to policies.google.com/privacy in Privacy Policy Section 4 |
| YouTube ToS referenced in Terms of Service | ✅ | ToS Section 5 |
| Google API Services User Data Policy compliance | ✅ | Limited Use statement in Privacy Policy Section 4 |
| YouTube data retention policy documented | ✅ | Privacy Policy Section 5 — deleted within 30 days of revocation |
| Revocation instructions for users | ✅ | Privacy Policy Section 8 — myaccount.google.com/permissions |
| AI content labeling for YouTube | ✅ | ToS Section 6c |
| YouTube API data deletion on revocation | ✅ | Privacy Policy Section 6 |
| Domain verified in Google Search Console | ⬜ | Ron needs to verify scribario.com |
| OAuth Consent Screen configured | ⬜ | Needs Google Cloud project |
| privacy@scribario.com email | ⬜ | Ron setting up forwarding |
