# Scribario — Setup Guide

This guide covers everything needed to run Scribario: local development, VPS deployment, and Postiz setup.

---

## Prerequisites

- Python 3.11 or higher
- [Supabase](https://supabase.com/) account (free tier is sufficient for development)
- [Postiz](https://postiz.app/) instance (self-hosted via Docker — see below)
- A Linux VPS for production (tested on Ubuntu 22.04 / Hostinger)

---

## Required API Keys

You will need accounts and API keys for the following services before Scribario will function:

| Service | Where to get it | Used for |
|---|---|---|
| **Telegram Bot Token** | [@BotFather](https://t.me/BotFather) on Telegram | Bot identity + message handling |
| **Anthropic API Key** | [console.anthropic.com](https://console.anthropic.com/) | Caption + brand voice generation |
| **Kie.ai API Key** | [kie.ai](https://kie.ai/) | Image generation (Nano Banana 2) |
| **Supabase URL + Keys** | Supabase project settings | Database + storage + queues |
| **Postiz API Key** | Postiz admin settings | Social media publishing |

---

## Environment Variables

Create a `.env` file in the project root. All variables are loaded via pydantic-settings.

```env
# ── Supabase ──────────────────────────────────────────────────────────────
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJ...                  # Public anon key (limited access)
SUPABASE_SERVICE_ROLE_KEY=eyJ...          # Service role key (full access — keep secret)

# ── Telegram ──────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=123456789:ABCdef...    # From @BotFather

# ── Anthropic (Claude) ────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-...             # From console.anthropic.com

# ── Kie.ai (Image Generation) ─────────────────────────────────────────────
KIE_AI_API_KEY=...                        # From kie.ai dashboard

# ── Meta (Facebook / Instagram / Threads) ─────────────────────────────────
FACEBOOK_APP_ID=...                       # Meta Developer App ID
FACEBOOK_APP_SECRET=...                   # Meta Developer App Secret

# ── Postiz (Social Publishing) ────────────────────────────────────────────
POSTIZ_URL=https://postiz.yourdomain.com  # Your self-hosted Postiz URL
POSTIZ_API_KEY=...                        # From Postiz admin settings
POSTIZ_ORG_ID=...                         # Your Postiz organization UUID
POSTIZ_SESSION_TOKEN=...                  # Postiz session cookie (for certain APIs)

# ── Worker Settings ───────────────────────────────────────────────────────
MAX_WORKER_CONCURRENCY=3                  # Max concurrent jobs (default: 3)
WORKER_POLL_INTERVAL_SECONDS=5            # Queue poll interval (default: 5)

# ── ElevenLabs (Phase 2 — optional) ──────────────────────────────────────
ELEVENLABS_API_KEY=...                    # Leave empty until needed
```

**Security notes:**
- Never commit `.env` to version control
- The `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS — treat it like a root password
- On VPS, store `.env` at `/opt/scribario/.env` with `chmod 600`

---

## Local Development Setup

### 1. Clone and install

```bash
git clone https://github.com/your-org/scribario.git
cd scribario

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt   # for testing + linting
```

### 2. Configure Supabase

Create a new Supabase project and note your project URL and keys from the project settings.

Apply all migrations:

```bash
# Install Supabase CLI if needed
npm install -g supabase

supabase login
supabase link --project-ref your-project-id

# Apply all migrations
supabase db push
```

Or apply migrations manually via the Supabase SQL editor — all migration files are in `supabase/migrations/`.

### 3. Create your `.env`

Copy and fill in the template above. For local development, you can leave `POSTIZ_URL` pointing to your production Postiz instance or run Postiz locally (see below).

### 4. Run the bot

```bash
python -m bot.main
```

### 5. Run the worker (separate terminal)

```bash
python -m worker.main
```

### 6. Test the flow

1. Open Telegram and search for your bot (the token from @BotFather)
2. Send `/start` to begin onboarding
3. Complete brand setup
4. Send a content request: `"Post something about our product"`
5. Wait ~30 seconds for the preview to arrive
6. Tap Approve — your post will be queued for publishing

---

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=term-missing

# Run a specific test file
pytest tests/test_caption_gen.py -v

# Run with verbose output
pytest -v
```

The test suite uses `pytest-asyncio` with `asyncio_mode = "auto"` — all async tests run automatically.

**Linting and type checking:**

```bash
# Lint with ruff
ruff check .

# Format check
ruff format --check .

# Type check with mypy
mypy . --strict
```

---

## VPS Deployment

This guide assumes Ubuntu 22.04 on your VPS. The production VPS runs at `31.97.13.213`.

### 1. Initial server setup

```bash
ssh root@your-vps-ip

apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx
```

### 2. Deploy the application

```bash
mkdir -p /opt/scribario
cd /opt/scribario
git clone https://github.com/your-org/scribario.git .

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
nano .env  # fill in all values
chmod 600 .env
```

### 4. Create systemd service for the bot

```bash
cat > /etc/systemd/system/scribario-bot.service << 'EOF'
[Unit]
Description=Scribario Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/scribario
EnvironmentFile=/opt/scribario/.env
ExecStart=/opt/scribario/.venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 5. Create systemd service for the worker

```bash
cat > /etc/systemd/system/scribario-worker.service << 'EOF'
[Unit]
Description=Scribario Background Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/scribario
EnvironmentFile=/opt/scribario/.env
ExecStart=/opt/scribario/.venv/bin/python -m worker.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 6. Enable and start services

```bash
systemctl daemon-reload

systemctl enable scribario-bot
systemctl enable scribario-worker

systemctl start scribario-bot
systemctl start scribario-worker

# Check status
systemctl status scribario-bot
systemctl status scribario-worker

# Follow logs
journalctl -u scribario-bot -f
journalctl -u scribario-worker -f
```

### 7. Deploying updates

```bash
cd /opt/scribario
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt

systemctl restart scribario-bot
systemctl restart scribario-worker
```

---

## Postiz Setup

Postiz is the self-hosted social media publishing engine. It runs in Docker.

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
```

### 2. Clone and configure Postiz

```bash
mkdir -p /opt/postiz
cd /opt/postiz

# Download the official docker-compose
curl -o docker-compose.yml https://raw.githubusercontent.com/gitroomhq/postiz-app/main/docker-compose.yaml

# Create .env for Postiz
cat > .env << 'EOF'
MAIN_URL=https://postiz.yourdomain.com
FRONTEND_URL=https://postiz.yourdomain.com
NEXT_PUBLIC_BACKEND_URL=https://postiz.yourdomain.com/api
JWT_SECRET=your-random-secret-here
DATABASE_URL=postgresql://postiz:postiz@postiz-db:5432/postiz
REDIS_URL=redis://postiz-redis:6379
BACKEND_INTERNAL_URL=http://postiz-backend:3000
IS_GENERAL=true
EOF

docker compose up -d
```

### 3. Configure nginx for Postiz

```bash
cat > /etc/nginx/sites-available/postiz << 'EOF'
server {
    listen 80;
    server_name postiz.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        client_max_body_size 50M;
    }
}
EOF

ln -s /etc/nginx/sites-available/postiz /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. SSL with Let's Encrypt

```bash
certbot --nginx -d postiz.yourdomain.com

# Certbot will automatically modify your nginx config and set up renewal
# Verify auto-renewal works:
certbot renew --dry-run
```

### 5. Connect your social accounts

1. Open `https://postiz.yourdomain.com` in your browser
2. Create an admin account
3. Go to Settings → Integrations
4. Connect Facebook, Instagram, and other platforms via OAuth
5. Note your Postiz API key from Settings → API Keys
6. Add it to your Scribario `.env` as `POSTIZ_API_KEY`

---

## DNS Setup

Point your domain to the VPS for Postiz:

| Record Type | Name | Value |
|---|---|---|
| A | `postiz` | `your-vps-ip` |

If you want to run the bot API on a subdomain too:

| Record Type | Name | Value |
|---|---|---|
| A | `bot` | `your-vps-ip` |

DNS propagation typically takes 5-30 minutes.
