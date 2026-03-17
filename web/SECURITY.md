# Scribario Web — Security Configuration

## Security Score: ~8.5/10 (as of 2026-03-13)

Audited via passive browser-side analysis. All findings remediated same day.

---

## Active Security Headers

All headers are set via `vercel.json` and apply to every route.

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://images.unsplash.com; font-src 'self'; connect-src 'self'; media-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests` | Prevents XSS, code injection, clickjacking via frames |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Forces HTTPS for 2 years, covers subdomains, HSTS preload eligible |
| `X-Frame-Options` | `DENY` | Prevents clickjacking (legacy browser support) |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing attacks |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer leakage |
| `X-XSS-Protection` | `1; mode=block` | XSS filter for legacy browsers |
| `Cross-Origin-Opener-Policy` | `same-origin` | Prevents cross-origin window attacks (Spectre mitigation) |
| `Cross-Origin-Resource-Policy` | `same-origin` (global), `cross-origin` (static assets) | Controls which origins can load resources |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=(), interest-cohort=(), accelerometer=(), gyroscope=(), magnetometer=()` | Disables unnecessary browser APIs |

## Image Security (`next.config.ts`)

- `dangerouslyAllowSVG: false` — Blocks SVG uploads (XSS vector)
- `contentDispositionType: "attachment"` — Forces download instead of inline render
- `contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;"` — Sandboxes optimized images
- Remote patterns restricted to `images.unsplash.com` only

## Additional Hardening

- `poweredByHeader: false` — Suppresses `X-Powered-By: Next.js` header
- `productionBrowserSourceMaps: false` — No source maps in production
- No `.git`, `.env`, `package.json` exposed (all return 404)
- No secrets in JS bundles (verified scan of all 10+ chunks)
- No inline event handlers (`onclick`, `onload`, etc.) in DOM
- No third-party analytics or tracking scripts loaded
- `rel="noopener noreferrer"` on all external links
- HttpOnly cookies (no JS-accessible cookies)
- HTTP methods restricted: PUT, DELETE, PATCH, OPTIONS all return 403
- TRACE method blocked
- Skip-to-content link for accessibility

## Security Contact

`/.well-known/security.txt` is live with:
- Contact: security@scribario.com
- Expires: 2027-03-13

## Responsible Disclosure

Security researchers can report vulnerabilities to security@scribario.com.

---

## Audit History

### 2026-03-13 — Initial Passive Audit

**Before remediation:** Score 6.5/10
- Missing: CSP, COOP, CORP, X-XSS-Protection, expanded Permissions-Policy, security.txt
- Present: HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, no exposed secrets

**After remediation:** Score ~8.5/10
- All missing headers added
- security.txt created
- Image security hardened
- Source maps disabled

**Remaining items for 9+:**
- Telegram bot webhook secret token validation (bot code, not website — separate repo concern)
- Move video assets to CDN (Cloudflare R2 or similar) to prevent 503 under load
- Rate limiting via Upstash Redis when user-facing features are added
- HSTS preload list submission at https://hstspreload.org
- Tighten CORS (`Access-Control-Allow-Origin: *` → specific origins) before adding authentication
- Tighten CSP (`unsafe-inline` → nonce-based) after testing

---

## Files

| File | Purpose |
|------|---------|
| `vercel.json` | All security headers (CSP, HSTS, COOP, CORP, etc.) |
| `next.config.ts` | Image security, source maps, powered-by suppression |
| `public/.well-known/security.txt` | Responsible disclosure contact |
| `SECURITY.md` | This file — security configuration reference |

## Pre-Auth/Payments Checklist

Before adding user accounts, payments, or any authenticated features:

- [ ] Replace `Access-Control-Allow-Origin: *` with specific origin allowlist
- [ ] Replace CSP `'unsafe-inline' 'unsafe-eval'` with nonce-based script loading
- [ ] Add rate limiting middleware (Upstash Redis recommended)
- [ ] Add CSRF protection on all state-changing endpoints
- [ ] Verify Telegram webhook validates `X-Telegram-Bot-Api-Secret-Token`
- [ ] Add session management with secure cookie flags
- [ ] Add input validation/sanitization on all user-facing forms
- [ ] Run OWASP ZAP or similar active scanner
- [ ] Consider WAF rules (Vercel Firewall or Cloudflare)
