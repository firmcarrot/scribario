# Meta — Facebook Pages + Instagram API Access

## Overview

Meta uses a single app framework covering both Facebook and Instagram. All publishing permissions require App Review and Business Verification.

## Prerequisites

1. Meta developer account at developers.facebook.com
2. Meta Business Portfolio (formerly Business Manager) at business.facebook.com
3. Publicly accessible app with a real use case
4. Privacy policy URL on a public domain (must cover data collection, use, storage, deletion from Meta APIs)
5. For Instagram: Professional Instagram account (Business or Creator) connected to a Facebook Page

## Required Permissions — Facebook Pages

| Permission | Purpose | Access Level |
|---|---|---|
| `pages_show_list` | List pages the user manages | Standard |
| `pages_read_engagement` | Read page content and metadata | Standard |
| `pages_manage_metadata` | Manage page settings | Advanced |
| `pages_manage_posts` | Create, edit, delete page posts | Advanced |

`pages_manage_posts` depends on both `pages_read_engagement` and `pages_show_list`. Request all of them.

Standard Access = auto-approved for test users. Advanced Access = requires App Review.

## Required Permissions — Instagram

| Permission | Purpose | Access Level |
|---|---|---|
| `pages_show_list` | Enumerate linked pages | Standard |
| `pages_read_engagement` | Read page data | Standard |
| `instagram_basic` | Read Instagram account profile + media | Standard |
| `instagram_content_publish` | Publish photos, videos, reels, carousels, stories | Advanced |

**Alternative (Instagram Login Flow):**
- `instagram_business_basic` (replaces `instagram_basic`)
- `instagram_business_content_publish` (replaces `instagram_content_publish`)

Both flows give the same capability. Facebook Login flow is required if you also need Facebook Page access.

## Step-by-Step Process

### Step 1: Development/Test Phase

All permissions work without App Review for users with a role on the app (Admin, Developer, Tester).

1. Create app at developers.facebook.com
2. Add test users: App Dashboard > Roles
3. Test the complete flow end-to-end with test users
4. Verify: OAuth login, page selection, posting, media upload all work

### Step 2: Business Verification

**Required since Feb 1, 2023 for Advanced Access permissions.**

1. Go to App Dashboard > Settings > Basic > Verification
2. Connect the app to a Business Portfolio (you must be an app Administrator)
3. Business Admin completes verification in Meta Business Manager
4. Documents typically required:
   - Business registration certificate or tax documents
   - Business domain email
   - Name must match across all documents
5. Timeline: 3-10 business days

**Do this BEFORE submitting App Review — submissions without it are immediately rejected.**

### Step 3: Privacy Policy and Data Use Checkup

1. Add Privacy Policy URL: App Dashboard > Settings > Basic
2. Complete Data Use Checkup: App Review > Data Use Checkup
3. Checkup asks how you use each category of data, retention periods, security measures

### Step 4: Submit App Review

1. Go to App Review > Permissions and Features
2. Select permissions, click "Request Advanced Access"
3. For EACH permission, provide:
   - **Written description**: Specific use case (not "I want to post to Facebook" — describe your product, users, and why they need this)
   - **Screencast video**: Demonstrates the permission in action
   - **Test credentials**: Working login to your app

### Step 5: Await Review

Typical review: 5-15 business days. Incomplete submissions take longer.

## Screencast Requirements (Critical — #1 Rejection Reason)

- Show the **complete user journey**: app login → OAuth flow (Meta login dialog visible) → feature that uses the permission → result
- Must show a **real, functional app** — not mockups
- Screen must be readable — 1080p minimum
- OAuth dialog must show YOUR app's name
- Format: MP4 preferred
- Keep it concise but thorough — show each requested permission in use

## Test User Setup

1. App Dashboard > Roles > Test Users
2. Create test users with test Facebook accounts
3. These accounts get advanced permissions without App Review
4. Instagram testing: App Review > Instagram Testers (connect real Professional account)

## Common Rejection Reasons

- Privacy policy is generic or missing data deletion/retention info
- Screencast does not show the Meta OAuth dialog
- Use case description is vague
- Business Verification not complete at submission time
- App has no real, accessible frontend (reviewer can't log in)
- Permissions requested exceed what the use case needs
- Data Use Checkup not completed

## Rate Limits

- Instagram publishing: 100 API-published posts per account per 24-hour rolling window
- Check remaining: `GET /{ig_user_id}/content_publishing_limit`

## Cost

Free — both App Review and Business Verification.

## Scribario-Specific Notes

- We use Postiz for posting, which handles the OAuth flow and API calls
- We need `pages_manage_posts` + `instagram_content_publish` at minimum
- Our privacy policy at scribario.com must specifically cover Meta data usage
- Screencast should show: Telegram bot → content generation → preview → approve → post appears on Facebook/Instagram
