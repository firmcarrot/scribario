# Scribario

**Your AI social media team — in a Telegram bot.**

[![Tests](https://img.shields.io/badge/tests-147%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Telegram](https://img.shields.io/badge/bot-%40ScribarioBot-2CA5E0?logo=telegram)](https://t.me/ScribarioBot)
[![Powered by Claude](https://img.shields.io/badge/AI-Claude%20API-orange)](https://www.anthropic.com/)
[![Built with Supabase](https://img.shields.io/badge/database-Supabase-3ECF8E?logo=supabase)](https://supabase.com)

---

Scribario turns a single Telegram message into a polished, platform-ready social media post — complete with an AI-generated image and brand-tuned caption — and publishes it automatically. No dashboard. No design tools. No copywriting. Just text your bot and approve what you like.

Business owners describe what they want to post. Scribario generates three unique caption + image combinations, each calibrated to the brand's voice and target audience. One tap approves the winner and schedules it for posting across Facebook, Instagram, and beyond.

---

## How It Works

```
You (Telegram)           Scribario                    The Internet
─────────────────────────────────────────────────────────────────────
"Post something about        ┌─────────────────────┐
 our weekend special"   ──►  │  Intent Parsing      │
                             │  (Claude API)        │
                             └────────┬────────────┘
                                      │
                             ┌────────▼────────────┐
                             │  Brand Voice Engine  │
                             │  Few-shot examples   │
                             │  Brand profile       │
                             └────────┬────────────┘
                                      │
                    ┌─────────────────┼──────────────────┐
                    ▼                 ▼                   ▼
            ┌──────────────┐ ┌──────────────┐   ┌──────────────┐
            │  Caption #1  │ │  Caption #2  │   │  Caption #3  │
            │  Image #1    │ │  Image #2    │   │  Image #3    │
            │  (Kie.ai)    │ │  (Kie.ai)    │   │  (Kie.ai)    │
            └──────┬───────┘ └──────┬───────┘   └──────┬───────┘
                   └────────────────┼──────────────────┘
                                    │
                             ┌──────▼──────┐
                             │  Preview in  │
                             │  Telegram    │
                             └──────┬───────┘
                                    │
                          You tap "Approve #2"
                                    │
                             ┌──────▼──────┐
                             │   Postiz     │
                             │  (self-host) │
                             └──────┬───────┘
                                    │
                          ┌─────────┴──────────┐
                          ▼                    ▼
                    Facebook Page         Instagram
                    ✓ Posted              ✓ Posted
```

---

## Features

- **Text-to-post in seconds** — describe it in plain English, get three professional options
- **Brand voice that actually sounds like you** — few-shot learning from your best past posts
- **3 image options per request** — generated in parallel by Kie.ai Nano Banana 2 (~25s)
- **One-tap approval** — Approve, Reject All, or Regenerate without leaving Telegram
- **Multi-platform publishing** — Facebook, Instagram, and more coming
- **Multi-tenant architecture** — every business gets isolated data, brand profiles, and posting credentials
- **Fully self-hosted** — your API keys, your data, your infrastructure
- **Reference photo support** — send a photo as creative direction for the image style
- **147 tests, 0 regressions** — TDD-first codebase, fully type-checked with mypy --strict

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot interface | [aiogram 3.x](https://aiogram.dev/) + [aiogram-dialog](https://github.com/Tishka17/aiogram_dialog) |
| Caption generation | [Anthropic Claude API](https://www.anthropic.com/) |
| Image generation | [Kie.ai Nano Banana 2](https://kie.ai/) |
| Social publishing | [Postiz](https://postiz.app/) (self-hosted) |
| Database + queues | [Supabase](https://supabase.com/) (Postgres + pgmq + pg_cron) |
| Background workers | Python async workers polling pgmq |
| Infrastructure | Hostinger VPS, systemd |
| Testing | pytest + pytest-asyncio |
| Type checking | mypy --strict |
| Linting | ruff |

---

## Demo

> **User:** "Post something about our weekend shrimp special. Make it feel exciting."

Scribario generates three options in ~30 seconds:

| Option | Caption Preview | Image |
|---|---|---|
| #1 | *"They said weekends were for resting. They clearly haven't tried our weekend special..."* | Cinematic overhead shot of shrimp dish |
| #2 | *"Most interesting weekend special in the world. Dare to try it? Stay hungry, my friends."* | Lifestyle photo with warm lighting |
| #3 | *"The VIP Club told us to keep this quiet. We didn't listen. Weekend special is LIVE."* | Bold product-forward composition |

User taps **Approve #2** → posted to Facebook + Instagram within seconds.

---

## Getting Started

See the full setup guide: **[docs/SETUP.md](docs/SETUP.md)**

**Prerequisites:**
- Python 3.11+
- Supabase account (free tier works for testing)
- Telegram bot token ([@BotFather](https://t.me/BotFather))
- Anthropic API key
- Kie.ai API key
- Postiz instance (Docker — [docs/SETUP.md#postiz](docs/SETUP.md#postiz-setup))

**Quick start:**

```bash
git clone https://github.com/your-org/scribario.git
cd scribario
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
python -m bot.main
```

---

## Documentation

| Document | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, database schema, queue system |
| [docs/SETUP.md](docs/SETUP.md) | Complete self-hosted setup guide (local + VPS + Postiz) |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | End-user guide for business owners using the bot |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Developer guide — standards, TDD, adding platforms |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Where we're going |
| [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) | Social platform integration status and credentials reference |

---

## Project Status

Scribario is in active development with a live beta deployment serving its first client.

- **Phase 1:** Complete — core pipeline, Facebook/Instagram posting, multi-tenant, 147 tests
- **Phase 2:** In progress — scheduling, style system, multi-platform expansion
- **Phase 3:** Planned — analytics, brand voice learning, agency dashboard

See the full roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## License

MIT — see [LICENSE](LICENSE)
