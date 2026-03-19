# Scribario — User Guide

Welcome to Scribario. This guide covers everything you need to know to use @ScribarioBot to create and publish content for your business.

---

## What Is Scribario?

Scribario is your AI social media team, delivered through Telegram. You describe what you want to post, Scribario creates three unique caption and image options tuned to your brand, and you pick the one you like. It posts automatically.

No design tools. No copywriting. No scheduling headaches. Just text your bot.

---

**Command Reference Diagram:** See [`scribario-commands.png`](./scribario-commands.png) for a visual overview of all commands and actions.

---

## Getting Started with @ScribarioBot

### Step 1: Open Telegram and find your bot

Search for `@ScribarioBot` in Telegram, or use the link your Scribario administrator provided.

### Step 2: Send /start

Type `/start` to begin. The bot will walk you through a quick brand setup — this takes about 2 minutes and only needs to be done once.

### Step 3: Answer the setup questions

The bot will ask about your business:
- **Business name and what you do**
- **Your brand tone** — how does your brand speak? (bold, warm, playful, professional, etc.)
- **Your target audience** — who are your customers?
- **Things to always include** — your tagline, a specific phrase, a call to action
- **Things to never do** — words to avoid, topics that are off-brand

This information trains Scribario's AI to generate content that actually sounds like your brand.

### Step 4: Connect your social accounts

Type `/connect` to link your Facebook, Instagram, or other platforms. You'll be walked through a quick authorization process. This only needs to be done once per platform.

---

## Sending Your First Post Request

Once setup is complete, just send a message describing what you want to post. Use plain English — no special commands needed.

**Examples:**

> "Post something about our weekend shrimp special"

> "We just restocked. Announce it with excitement."

> "It's National Hot Sauce Day. Make something fun."

> "Post a customer appreciation message — we just hit 500 orders."

> "We're hiring. Looking for a part-time kitchen assistant."

Scribario will acknowledge your request and start generating content. This typically takes 20-40 seconds.

---

## Understanding the 3 Preview Options

When content is ready, you'll receive three distinct options — each with a unique image and caption. They are based on the same intent but approach it differently in tone, angle, or visual style.

**Why three options?**

Because great content is often a matter of taste. Option #1 might be bold and punchy. Option #2 might be warm and story-driven. Option #3 might be product-forward and direct. You choose what fits the moment.

Each preview shows:
- The **full caption** (including hashtags if applicable)
- The **generated image** for that option
- The platform(s) it will be posted to

---

## Approving, Rejecting, Regenerating

After seeing your three options, you have four choices:

| Button | What it does |
|---|---|
| **Approve #1** / **#2** / **#3** | Sends that specific caption + image to your social accounts immediately |
| **Reject All** | Discards all three options. No post is made. |
| **Regenerate** | Discards all three and generates three completely new options from your original request |

**Tap to approve** — there is no confirmation step. Once you tap Approve, the post is queued for publishing. You will receive a confirmation message when it goes live.

---

## Connecting Social Platforms

Type `/connect` at any time to add or manage your connected social accounts.

Currently supported:
- **Facebook** (Pages)
- **Instagram** (Business accounts)

Coming soon: LinkedIn, Bluesky, TikTok, YouTube

For Facebook and Instagram, you'll be taken through a quick OAuth authorization flow in your browser. After authorizing, you'll be returned to the bot automatically.

**Note:** You must be an admin of the Facebook Page or Instagram Business account you want to connect.

---

## Tips for Writing Great Prompts

The clearer your request, the better your content.

**Be specific about the occasion:**
> "It's the day before Thanksgiving. Post something warm and community-focused."

Rather than:
> "Post something for the holiday."

**Include the emotion you want:**
> "This should feel exciting — we're celebrating something."

**Mention what's different today:**
> "We just launched a new flavor. It's the first time we've had something sweet."

**Give context about the audience:**
> "This is for our VIP members who've been with us from the start."

**Tell Scribario what NOT to do:**
> "Don't make it too salesy — just make it feel genuine."

---

## Style Hints

You can include style hints in your message to guide the image generation:

| Hint | Effect |
|---|---|
| `photorealistic` | Realistic photography style |
| `cinematic` | Movie-quality lighting and drama |
| `illustrated` | Artistic, illustrated style |
| `flat design` | Clean, minimal graphic design |
| `overhead shot` | Top-down product photography |
| `lifestyle` | People enjoying your product in context |
| `bold colors` | High saturation, punchy palette |
| `dark moody` | Low-key, dramatic lighting |

**Example:**

> "Post about our sauce. Cinematic, dark moody, product-forward. Make it feel premium."

---

## Creating Video Content

You can create short-form video posts (Reels, Stories, TikToks, Shorts) directly from the bot. Just include a video-related word in your message and Scribario handles the rest.

**Trigger words:** Include "video", "reel", "clip", or "animate" in your request.

**Examples:**

> "Make a video reel about our weekend brunch special"

> "Animate something fun for National Donut Day"

> "Create a short clip showing our new product line"

**Orientation is automatic:**

- Words like "reel", "story", "tiktok", or "shorts" produce **vertical video (9:16)**
- Other video requests default to landscape

**What you get:**

Scribario generates a video along with 3 caption options — the same approval flow you already know. Tap Approve on the caption you like and the video posts with that caption. Tap Regenerate to get a brand new video and new captions.

**Video from an image preview:**

If you already have an image preview and want to turn it into a video instead, tap the **Make Video** button on any option. The bot will generate a video using that image's direction.

**How long does it take?**

Video generation takes 1-3 minutes (longer than image posts). The bot will let you know it's working.

---

## Autopilot Mode

Autopilot lets the AI generate and post content for you on a schedule — so you can set it and forget it.

### Setting Up Autopilot

Type `/autopilot` and tap **Set Up Autopilot**. You'll choose:

1. **Mode:**
   - **Smart Queue (recommended)** — Scribario generates content and sends you a preview. If you don't reject within 2 hours, it posts automatically. You can approve early, reject, or edit.
   - **Full Autopilot** — Scribario generates and posts without waiting. You get a notification after.

2. **Schedule:** Tell it when to post in plain English:
   - "daily at 10am"
   - "Mon/Wed/Fri at 10am"
   - "weekdays at 9am"
   - "every other day at 3pm"

3. **Platforms:** All connected, or a specific platform.

### How Smart Queue Works

When it's time to post, Scribario generates content and sends you a preview — just like a manual post. The difference: there's a countdown. If you don't reject within 2 hours, it posts automatically.

You'll see a message like:

> 🤖 Autopilot generated a new post:
>
> [Image + 3 caption options]
>
> ⏰ Auto-posting in 2 hours unless you reject.

You can:
- **Approve early** — tap Approve on any option
- **Reject** — tap Reject to cancel this post
- **Do nothing** — it auto-posts the first option after the timeout

### Safety Features

- **Warmup period:** Your first 5 posts always use Smart Queue, even if you chose Full Autopilot. This gives you a chance to see what the AI generates before trusting it fully.
- **Daily limit:** Default 3 posts/day (you can change this)
- **Cost cap:** Default $50/month — Scribario pauses if it hits the cap
- **Auto-pause:** If something goes wrong 3 times in a row, autopilot pauses and notifies you

### Managing Autopilot

| Command | What it does |
|---|---|
| `/autopilot` | Show status, change settings, pause, or turn off |
| `/pause` | Immediately stop all autopilot activity |
| `/resume` | Restart autopilot on its schedule |

### Weekly Digest

Every Sunday morning, you'll get a summary:
- How many posts were created and published
- How much it cost
- Any failures

---

## Billing & Subscription

### Plans

| Plan | Price | Image Posts | Video Credits |
|---|---|---|---|
| **Free Trial** | Free | 5 posts total | 1 video total |
| **Starter** | $29/mo ($278/yr) | 15/mo | 5/mo |
| **Growth** | $59/mo ($566/yr) | 40/mo | 15/mo |
| **Pro** | $99/mo ($950/yr) | 100/mo | 40/mo |

Annual plans save 20%. Credits reset on your billing anniversary (not the 1st of the month).

### Billing Commands

| Command | What it does |
|---|---|
| `/subscribe` | Choose a plan and subscribe via Stripe Checkout |
| `/upgrade` | Upgrade to a higher tier (prorated) |
| `/topoff` | Buy extra credits: +10 images ($5), +5 videos ($12) — max 3 per category/month |
| `/usage` | See your current usage with visual progress bars |
| `/billing` | Open the Stripe Customer Portal to manage payment methods, view invoices, or cancel |

### How Usage Works

- **Image posts** and **video credits** reset each billing cycle
- **Bonus credits** (from top-offs) persist until used — they never expire or reset
- At **80% usage**, Scribario sends a warning so you can top off before running out
- When you **cancel**, your subscription stays active until the end of the current billing period — no refunds, but you keep what you paid for

### Upgrading and Downgrading

- **Upgrade:** Takes effect immediately. You get the new tier's credit limits right away. Stripe prorates the charge.
- **Downgrade:** Managed through the Customer Portal (`/billing`). Takes effect at next billing cycle.

---

## Sending Reference Photos

You can send a photo directly to the bot to use as creative direction for your images. The AI will use your photo as a style reference — matching the lighting, color tone, composition, or subject matter.

Just send the photo before or along with your content request. The bot will confirm it's been saved and use it as a reference for the next generation.

---

## FAQ

**How long does it take to generate content?**

Image posts typically take 20-40 seconds. Caption generation and image generation run in parallel, so the total wait is roughly the image generation time (~25 seconds for three images). Video requests take 1-3 minutes.

**Can I edit the caption before it posts?**

Yes — tap the ✏️ Edit button on any option to revise the caption. You'll see an updated preview before approving. You can also Regenerate for completely new options, or reject and send a new request with more specific guidance.

**What happens if I reject all three?**

Nothing is posted. You can send a new request at any time.

**Can I schedule posts for later?**

Yes — include a date and time in your request (e.g., "post this Friday at 9am") and Scribario will queue it automatically. You'll get a confirmation with the scheduled time.

**Can I post to multiple platforms at once?**

Yes — when you /connect multiple accounts, Scribario will post to all connected platforms when you approve.

**How does the brand voice work?**

Scribario uses your brand profile (set up during onboarding) plus examples of your best past posts to generate content that sounds like you. The more context you give during setup, the better it gets.

**Can I update my brand profile?**

Yes — type `/brand` to update your brand settings at any time.

**What if the image isn't quite right?**

Choose Regenerate to get three completely new options. Or include style hints in your request (see above) to guide the image direction.

**Can Scribario post automatically without me approving each time?**

Yes — use `/autopilot` to set up Autopilot Mode. You can choose Smart Queue (preview with auto-post after 2 hours) or Full Autopilot (completely hands-free). See the Autopilot Mode section above.

**Is my content saved?**

Yes — all requests, drafts, and approved posts are saved to your account. Post history and analytics are coming in Phase 2.

**What happens when I run out of credits?**

Scribario will let you know when you're at 80% usage. If you hit the limit, use `/topoff` to buy more credits instantly, or wait for your next billing cycle to reset. Bonus credits from top-offs never expire.

**How do I cancel my subscription?**

Type `/billing` to open the Stripe Customer Portal. You can cancel there. Your access continues until the end of the current billing period — no refunds, but you keep what you paid for.

**When do my credits reset?**

On your billing anniversary — the same day each month that you subscribed. Not the 1st of the month.

**Who can use my bot?**

Only Telegram accounts linked to your Scribario account. Contact your Scribario administrator to add additional team members.
