#!/usr/bin/env bash
# Refresh Postiz session token by calling the login API.
# Run via systemd timer every 6 hours.
set -euo pipefail

ENV_FILE="/opt/scribario/.env"
LOGIN_JSON="/tmp/postiz_login.json"
POSTIZ_URL="https://postiz.scribario.com"

# Read credentials from env
source "$ENV_FILE"

# Build login payload
cat > "$LOGIN_JSON" <<EOF
{"email":"${POSTIZ_EMAIL}","password":"${POSTIZ_PASSWORD}","provider":"LOCAL"}
EOF

# Call login API, extract auth cookie
RESPONSE=$(curl -s -D- "$POSTIZ_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d @"$LOGIN_JSON" 2>&1)

rm -f "$LOGIN_JSON"

# Extract token from Set-Cookie header
NEW_TOKEN=$(echo "$RESPONSE" | grep -oP 'Set-Cookie: auth=\K[^;]+')

if [ -z "$NEW_TOKEN" ]; then
  echo "ERROR: Failed to get new Postiz session token"
  echo "$RESPONSE" | head -5
  exit 1
fi

# Update .env file
sed -i "s|^POSTIZ_SESSION_TOKEN=.*|POSTIZ_SESSION_TOKEN=$NEW_TOKEN|" "$ENV_FILE"

echo "OK: Postiz session token refreshed at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Restart services to pick up new token
systemctl restart scribario-bot scribario-worker
echo "OK: Services restarted"
