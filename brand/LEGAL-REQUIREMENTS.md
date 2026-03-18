# Scribario Legal Documents — Requirements for Platform Approval

## Overview

Both documents (ToS + Privacy Policy) must be:
- Live on public URLs (scribario.com/terms, scribario.com/privacy)
- No login wall, no geo-blocking
- HTML pages (not PDF-only)
- Must be live BEFORE submitting any platform app review

## Platform Review Sequence

1. Get website live with ToS + Privacy Policy pages
2. Meta App Review (Facebook + Instagram) — needs Data Deletion Callback URL
3. LinkedIn Marketing API — needs privacy/security review
4. TikTok audit — compliance review, limited to 5 users/24hr until approved
5. Bluesky — no formal review, just comply with developer guidelines

---

## Terms of Service — Required Sections

### 1. Introduction & Acceptance
- Legal entity name
- Effective date + version number
- Acceptance mechanism (account creation / first use)
- Continued use after modification = acceptance
- Minimum age: 18 (simplest — avoids COPPA/GDPR age variation issues)

### 2. Description of Service
- AI content generation (captions via Claude/Anthropic, images via Kie.ai)
- OAuth connection to social media accounts
- Automated posting on user's behalf
- Explicit AI disclosure (required by EU AI Act Article 50, TikTok, Meta, FTC)

### 3. Account Registration & Security
- User responsible for credentials
- No account sharing
- Accurate information required
- Compromised account notification obligation

### 4. Authorized Use & Prohibited Conduct
- Must comply with each connected platform's own ToS
- No spam, inauthentic behavior, coordinated manipulation
- No deceptive AI content / impersonation
- No IP infringement
- No illegal use
- No reverse-engineering OAuth tokens

### 5. Third-Party Platform Connections (OAuth)
- How OAuth works (user grants permission directly to platform)
- Scribario never sees/stores platform passwords
- Only minimum necessary permissions requested
- User can revoke access anytime via platform settings
- Scribario not affiliated with/endorsed by any platform
- Platforms may change APIs — service availability may be affected

### 6. AI-Generated Content

**6a. Content Ownership**
- AI outputs are not guaranteed copyrightable (U.S. Copyright Office position)
- User gets broad license to use generated content
- Other users may receive similar outputs
- Kie.ai's IP terms apply to generated images

**6b. Accuracy & Liability**
- AI content may be inaccurate, misleading, inappropriate
- User solely responsible for reviewing before posting
- No warranty of platform compliance, advertising standards, or legal compliance
- No liability for brand damage from AI content

**6c. AI Disclosure Obligation (on the user)**
- TikTok: synthetic media label required
- EU AI Act Article 50 (August 2026): AI content labeling required
- Meta: AI content labeling for ads
- User responsible for adding required labels

### 7. User Content License
- License to Scribario to process uploaded content solely to provide service
- User confirms they own/have rights to uploads
- DMCA notice-and-takedown procedure

### 8. Subscription, Payment, Cancellation
- Tiers and pricing
- Auto-renewal disclosure (FTC Negative Option Rule)
- Refund policy
- What happens to data on cancellation

### 9. Data Retention & Deletion
- Retention period after cancellation
- User right to request deletion
- **Meta: Data Deletion Callback** (POST endpoint receiving signed requests)
- **LinkedIn: Profile data max 24hr, activity data max 48hr**
- GDPR: respond within 30 days
- CCPA: respond within 45 days

### 10. Intellectual Property
- Scribario brand/platform IP belongs to Scribario
- Platform API data remains platform's property
- No copyright guarantee on AI outputs

### 11. Disclaimers & Limitation of Liability
- "As is" without warranties
- No guarantee posts will publish successfully
- No warranty on AI content accuracy/originality
- Liability cap: fees paid in prior 12 months
- Exclude consequential/punitive damages
- Carve out GDPR liability (can't be contracted away in EU)

### 12. Indemnification
- User indemnifies Scribario for claims from:
  - Content they post
  - Platform ToS violations
  - Legal violations
  - IP infringement

### 13. Termination
- Grounds (ToS violation, non-payment, API revocation)
- 30 days notice for without-cause termination
- Immediate for cause (illegal activity, abuse)
- Data export window after termination

### 14. Modifications
- Right to modify terms
- 30 days notice for material changes
- Notification method (email)
- Continued use = acceptance

### 15. Governing Law & Disputes
- Jurisdiction
- Arbitration clause (with EU/UK carve-out)
- CCPA rights cannot be waived

---

## Privacy Policy — Required Sections

### 1. Controller Identity
- Legal entity name, address, contact
- privacy@scribario.com (or equivalent)
- Effective date

### 2. Data Collected

| Category | Data |
|---|---|
| Account | Name, email, password hash |
| Billing | Via Stripe (disclose as subprocessor) |
| Social connections | OAuth tokens (encrypted), account IDs, page IDs |
| Platform data | Profile data, account info received via API |
| User uploads | Brand guidelines, reference images, prompts |
| AI interaction | Prompts to Claude/Kie.ai, generated outputs, approve/reject signals |
| Usage/technical | IP, device type, feature usage, Telegram user ID |

### 3. How Data Is Used (with GDPR legal basis)
- **Contract performance:** Content gen, posting, OAuth management
- **Legitimate interests:** Analytics, fraud prevention, service improvement
- **Legal obligation:** Tax records, lawful requests
- **Consent:** Marketing emails
- **NOT used for:** Advertising to third parties, training AI models on user content

### 4. Data Sharing & Subprocessors

| Subprocessor | Data Received | Purpose |
|---|---|---|
| Anthropic (Claude) | Prompts, brand data | Caption generation |
| Kie.ai | Image prompts | Image generation |
| Postiz | Post content, schedules | Social media posting |
| Supabase | All stored data | Database hosting |
| Hostinger | All application data | Server hosting |
| Stripe | Billing data | Payment processing |
| Meta, TikTok, LinkedIn, Bluesky | Post content | Publishing via API |

- State: "We do not sell your data" (CCPA requirement)
- Anthropic API does NOT use inputs for training by default — state this

### 5. Data Retention
- Account data: duration of account + 90 days
- Billing records: 7 years (tax compliance)
- **LinkedIn profile data: max 24 hours**
- **LinkedIn social activity data: max 48 hours**
- Backups: [define retention]

### 6. Data Deletion & Meta Callback
- User right to request deletion (email or in-app)
- **Meta Data Deletion Callback URL** — mandatory endpoint
- Timeline: 30 days (GDPR), 45 days (CCPA)
- What's deleted vs retained (anonymized aggregates, billing records)

### 7. User Rights
**GDPR:** Access, rectify, erase, restrict, port, object
**CCPA:** Know, delete, opt-out of sale, correct, non-discrimination
- Contact: privacy@scribario.com
- Response: 30 days GDPR, 45 days CCPA

### 8. Security
- Encryption in transit (TLS) and at rest (OAuth tokens)
- Access controls
- Breach notification: 72hr to supervisory authority (GDPR)
- No guarantee of absolute security

### 9. International Data Transfers
- Servers in US (Supabase us-east-1, Hostinger VPS)
- EU-U.S. Data Privacy Framework or Standard Contractual Clauses

### 10. Cookies
- Session cookies, auth tokens
- Analytics (if any)
- Cookie consent for EU users (non-essential cookies)

### 11. Children's Privacy
- Not directed to users under 18
- No knowing collection from minors
- Immediate deletion if discovered

### 12. AI-Specific Disclosures
- Uses Claude (Anthropic) for captions, Kie.ai for images
- User prompts are NOT used to train models (per Anthropic API terms)
- AI content may not be copyrightable
- EU AI Act Article 50 compliance

### 13. Bluesky/AT Protocol Disclosures
- Content posted to Bluesky is public and may replicate across AT Protocol servers
- Deletion not guaranteed on decentralized network

### 14. Changes to Policy
- 30 days notice for material changes
- Retain historical versions (Meta requirement)

### 15. Contact
- privacy@scribario.com
- Mailing address
- EU users: right to complain to supervisory authority

---

## Implementation Checklist

- [ ] ToS page live at scribario.com/terms
- [ ] Privacy Policy page live at scribario.com/privacy
- [ ] Meta Data Deletion Callback endpoint built and registered
- [ ] privacy@scribario.com email working
- [ ] Cookie consent banner for EU users
- [ ] Subprocessor list maintained (link from privacy policy)
- [ ] DMCA agent registered with U.S. Copyright Office (if hosting user content)
- [ ] Historical policy versions retained
- [ ] Both pages crawlable (no login wall, no geo-block)
