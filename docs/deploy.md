# WebStaffr — Deploy Guide

## Backend (FastAPI)

### Option A: Railway (recommended — 10 min)

1. Push repo to GitHub
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub → select `webstaffr`
3. Add environment variables (copy from `.env.example`, fill in real values)
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Railway auto-deploys on every push to `main`

Your API: `https://webstaffr-production.up.railway.app`

---

### Option B: Render (free tier available)

1. [render.com](https://render.com) → New Web Service → Connect repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables → Deploy

---

### Local development

```bash
cp .env.example .env        # fill in your keys
uvicorn backend.main:app --reload --port 8000
open http://localhost:8000/dashboard
open http://localhost:8000/docs
```

---

## Agency Site (Netlify — separate site)

`frontend/landing/index.html` is a standalone static file — it deploys as its own
Netlify site, separate from the backend. No build step required.

```bash
# From repo root
cd frontend/landing
npx netlify deploy --prod --dir .
```

Or drag-and-drop the `frontend/landing/` folder at [app.netlify.com](https://app.netlify.com).

### netlify.toml for the agency site

Place this file inside `frontend/landing/` before deploying:

```toml
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options        = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy        = "strict-origin-when-cross-origin"

[[redirects]]
  from   = "/api/*"
  to     = "https://YOUR-BACKEND.up.railway.app/api/:splat"
  status = 200
```

Replace `YOUR-BACKEND` with your Railway or Render URL. This proxies
`/api/onboard` (the inline lead form endpoint) through Netlify so the
static site can reach the FastAPI backend without CORS issues.

**Recommended Netlify site name:** `webstaffr` → live at `webstaffr.netlify.app`
until the custom domain `webstaffr.com` is pointed.

---

## Client Sites (Netlify)

```bash
# Build from intake
python builder/site_generator.py --intake tests/fixtures/example_intake.json

# Deploy
cd clients/<biz_slug>_<timestamp>
npx netlify deploy --prod --dir .
```

---

## Environment Variable Reference

Every variable the codebase reads from `.env`, which agent uses it, and
what breaks if it is missing.

| Variable | Agent / Module | Required | Breaks If Missing |
|---|---|---|---|
| `OPENAI_API_KEY` | Receptionist, Lead Coordinator, Reputation Manager | **Yes** | All agents fall back to generic template messages (SMS still sends, but not personalized) |
| `TWILIO_ACCOUNT_SID` | Receptionist, Lead Coordinator, Reputation Manager | **Yes** | No SMS or voice — agents log error and return failure |
| `TWILIO_AUTH_TOKEN` | Receptionist, Lead Coordinator, Reputation Manager | **Yes** | Same as above — Twilio auth fails |
| `TWILIO_PHONE_NUMBER` | Receptionist, Lead Coordinator, Reputation Manager | **Yes** | SMS `from` number missing — Twilio rejects send |
| `SENDGRID_API_KEY` | Lead Coordinator | **Yes** | Email follow-up fails silently; SMS still fires |
| `SENDGRID_FROM_EMAIL` | Lead Coordinator | **Yes** | SendGrid rejects send without a verified from address |
| `SENDGRID_FROM_NAME` | Lead Coordinator | No | Falls back to `"WebStaffr"` |
| `DATABASE_URL` | `db/models.py` (all routes) | **Yes** | App fails to start — SQLAlchemy can't connect |
| `BASE_URL` | `builder/site_generator.py` | No | Lead capture JS in built sites points to `localhost:8000` |
| `APP_SECRET_KEY` | Future auth middleware | No | No current breakage; required before adding dashboard auth |
| `ENVIRONMENT` | Logging, CORS | No | Defaults to `development`; set to `production` on Railway/Render |
| `ZAPIER_SERVICETITAN_WEBHOOK_URL` | `routes/integrations.py` | No | ST sync skipped; leads still captured in WebStaffr DB |
| `ZAPIER_JOBBER_WEBHOOK_URL` | `routes/integrations.py` | No | Jobber sync skipped |
| `ZAPIER_HCP_WEBHOOK_URL` | `routes/integrations.py` | No | Housecall Pro sync skipped |
| `ST_CLIENT_ID` | `routes/integrations.py` | No (Phase 2) | Falls back to Zapier bridge automatically |
| `ST_CLIENT_SECRET` | `routes/integrations.py` | No (Phase 2) | Same |
| `ST_TENANT_ID` | `routes/integrations.py` | No (Phase 2) | Same |
| `ST_API_BASE` | `routes/integrations.py` | No | Defaults to `https://api.servicetitan.io` |

**Minimum viable `.env` for a working MVP** (agents active, FSM via Zapier):

```
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=hello@webstaffr.com
DATABASE_URL=sqlite:///./webstaffr.db
BASE_URL=https://your-backend-url.up.railway.app
ZAPIER_SERVICETITAN_WEBHOOK_URL=https://hooks.zapier.com/...
```

---

## Twilio Sandbox — Full Walkthrough

### Step 1: Buy a number

1. Log into [console.twilio.com](https://console.twilio.com)
2. Phone Numbers → Manage → Buy a number
3. Search for a local number in your target market (Phoenix: area code 602)
4. Purchase it (~$1.15/month)
5. Copy the number — this is `TWILIO_PHONE_NUMBER` in `.env`

### Step 2: Set the voice webhook

1. Phone Numbers → Manage → Active Numbers → click your number
2. Under **Voice & Fax** → **A Call Comes In** → set to **Webhook**
3. URL: `https://YOUR-BACKEND.up.railway.app/webhooks/voice/incoming`
4. Method: **HTTP POST**
5. Save

### Step 3: Test locally with ngrok

```bash
# Install ngrok (one-time)
brew install ngrok   # macOS
# or download from ngrok.com

# Start tunnel
ngrok http 8000

# ngrok output:
# Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000

# Paste the https URL into Twilio console:
# https://abc123.ngrok-free.app/webhooks/voice/incoming
```

### Step 4: Simulate a missed call

```bash
# Simulate Twilio posting to your webhook (replace CLIENT_PHONE with
# a number you've registered in the DB as a client's Twilio number)
curl -X POST http://localhost:8000/webhooks/voice/incoming \
  -d "To=+16025550192&From=+16025559999"
```

Expected behavior:
1. TwiML response plays the hold message
2. Receptionist agent fires in background
3. SMS sent to `+16025559999` within ~3 seconds
4. Lead created in DB — visible in dashboard at `http://localhost:8000/dashboard`

### Step 5: Verify in dashboard

```bash
open http://localhost:8000/dashboard
# Agent Activity Feed should show:
# 📞 Receptionist · missed_call · ✓ Success
```

---

## ServiceTitan Phase 1 (Zapier bridge)

1. Zapier → New Zap → **Webhooks by Zapier** → Catch Hook → copy URL
2. Action 1: **ServiceTitan** → Create/Update Customer — map `customer_name`, `customer_phone`, `customer_email`
3. Action 2: **ServiceTitan** → Create Job — map `job_type` to Business Unit, `job_source = "WebStaffr"`, `job_notes` to Summary
4. Paste URL into `.env` as `ZAPIER_SERVICETITAN_WEBHOOK_URL`

All new WebStaffr leads now auto-create ST customers + jobs. No ST credentials required.

See `docs/servicetitan_integration.md` for full payload schema and field mapping.

---

## Register a Client (API)

```bash
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "biz_name": "Desert Air HVAC",
    "phone": "(602) 555-0192",
    "email": "owner@desertairhvac.com",
    "industry": "HVAC",
    "service_area": "Phoenix, AZ",
    "plan": "growth"
  }'
# Returns: {"id": "uuid-...", "biz_name": "Desert Air HVAC", "plan": "growth"}
# Save the id — it is CLIENT_ID in all subsequent commands
```

---

## First Client Onboarding Checklist

The 10 steps from signed contract to live AI office.

```
[ ] 1. Register client in DB
        POST /api/clients with biz_name, phone, email, industry, service_area, plan
        Save the returned client_id

[ ] 2. Buy and configure Twilio number
        Purchase a local number for the client's market
        Set TWILIO_PHONE_NUMBER for this client's configuration
        Set voice webhook: POST https://YOUR-BACKEND/webhooks/voice/incoming

[ ] 3. Set Zapier webhook (if client uses ServiceTitan / Jobber / HCP)
        Create Zapier Catch Hook → FSM actions Zap
        Add ZAPIER_*_WEBHOOK_URL to .env and redeploy

[ ] 4. Run intake form or build site manually
        Option A: Client completes intake/intake.html (auto-triggers build)
        Option B: python builder/site_generator.py --intake client.json

[ ] 5. Verify built site
        Open clients/<slug>_<timestamp>/index.html
        Check: biz name, phone, services, colors all correct
        Check: webstaffr-manifest.json has correct client_id and plan

[ ] 6. Deploy client site to Netlify
        cd clients/<slug>_<timestamp>
        npx netlify deploy --prod --dir .
        Note the live URL

[ ] 7. Update client record with site URL
        curl -X PATCH http://localhost:8000/api/clients/<CLIENT_ID> \
          -H "Content-Type: application/json" \
          -d '{"site_url": "https://their-site.netlify.app"}'

[ ] 8. Test lead form end-to-end
        Submit the contact form on the live client site
        Verify: SMS fires to test number within 60 seconds
        Verify: Lead appears in dashboard feed
        Verify: ST sync shows "Synced" status (if FSM configured)

[ ] 9. Test missed call
        Call the client's Twilio number from a test phone
        Verify: TwiML voice message plays
        Verify: SMS text-back arrives within 5 seconds
        Verify: Lead logged in dashboard

[ ] 10. Hand off to client
         Share dashboard URL: https://YOUR-BACKEND/dashboard
         Send client their site URL and Twilio number
         Confirm they can see live leads and agent activity
         Schedule 30-day check-in call
```

---

## Test Agent Actions

```bash
# Missed call → instant SMS
curl -X POST http://localhost:8000/webhooks/voice/incoming \
  -d "To=+16025550192&From=+16025559999"

# Lead form → SMS + email + ST sync
curl -X POST http://localhost:8000/webhooks/lead-form \
  -H "Content-Type: application/json" \
  -d '{"client_id":"CLIENT_ID","name":"John Smith","phone":"+16025559876","message":"AC not cooling"}'

# Job complete → review request
curl -X POST http://localhost:8000/webhooks/job-complete \
  -H "Content-Type: application/json" \
  -d '{"client_id":"CLIENT_ID","customer_phone":"+16025559876","customer_name":"John Smith","job_type":"AC Repair","google_review_link":"https://g.page/r/your-link"}'
```

---

## Investor Demo Script

1. `open http://localhost:8000/dashboard`
2. `open http://localhost:8000/docs` — show full live API
3. `open intake/intake.html` — fill out form as a contractor
4. Watch lead appear in dashboard feed
5. Show ST integration banner — "Phase 1 active"
6. Show site build: `python builder/site_generator.py --intake tests/fixtures/example_intake.json`
7. Open built site in `clients/` folder
