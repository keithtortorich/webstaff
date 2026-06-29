# WebStaffr — AI Office Staff for Home Service Contractors

> *We run the office while contractors run the business.*

**Beachhead:** Phoenix HVAC | **Stack:** FastAPI · SQLite→Postgres · Twilio · OpenAI · Netlify

---

## What It Does

WebStaffr builds a free AI-powered website for home service contractors and deploys a named AI workforce that runs their front office 24/7. Contractors keep their existing field-service software (ServiceTitan, Jobber, Housecall Pro). WebStaffr makes sure more customers reach it.

---

## AI Workforce

| Employee | Department | Trigger | Action |
|---|---|---|---|
| **Receptionist** | Front Office | Missed call | Instant personalized SMS callback |
| **Lead Coordinator** | Front Office | Form submit | SMS + email within 60 seconds |
| **Reputation Manager** | Marketing | Job complete | Google review request SMS |
| **Sales Consultant** | Sales | Estimate request | Follow-up email with proposal |
| **Office Manager** | Operations | Always on | Hosting, integrations, site health |

---

## Workforce Plans

| Plan | Price | Staff |
|---|---|---|
| **Essentials** | $197/mo | Office Manager |
| **AI Office Staff** *(recommended)* | $497/mo | + Receptionist, Lead Coordinator, Reputation Manager, Sales Consultant |
| **AI Business Manager** | $997/mo | + Marketing Coordinator, Growth Manager, Local SEO, CRM Automation |

---

## Platform Integrations

WebStaffr integrates with FSM platforms contractors already use — not replaces them.

| Platform | Phase | Status |
|---|---|---|
| ServiceTitan | Phase 1 (Zapier bridge) | Active in MVP |
| ServiceTitan | Phase 2 (native OAuth API) | Weeks 4–8 |
| Jobber | Phase 2 | Same architecture |
| Housecall Pro | Phase 2 | Same architecture |
| ST App Marketplace | Phase 4 | Months 3–6 |

> *"What happens when ServiceTitan builds this?" → We want them to. It validates the category. We're the front-office specialist that benefits from their distribution.*

---

## Architecture

```
Trigger (call / form / job complete)
    ↓
FastAPI webhook receiver  (backend/main.py)
    ↓
Agent handler fires  (backend/agents/)
    ↓
OpenAI personalizes → Twilio / SendGrid executes
    ↓
DB logs result → Dashboard updates
```

Each AI employee is one file, one trigger, one OpenAI call, one API action. No orchestration framework. Fully debuggable. Near-zero marginal cost at scale.

---

## Project Structure

```
webstaffr/
├── backend/
│   ├── main.py                      # FastAPI entry point
│   ├── agents/
│   │   ├── receptionist.py          # Missed call → SMS
│   │   ├── lead_coordinator.py      # Form submit → SMS + email
│   │   ├── reputation_manager.py    # Job complete → review SMS
│   │   └── sales_consultant.py      # Estimate → follow-up email
│   ├── routes/
│   │   ├── webhooks.py              # Twilio + form inbound
│   │   ├── dashboard.py             # Admin API
│   │   └── integrations.py          # ServiceTitan / Jobber / HCP
│   └── db/
│       ├── models.py                # SQLAlchemy schema
│       └── crud.py                  # DB helpers
├── builder/
│   └── site_generator.py            # Intake JSON → deployed site
├── frontend/
│   └── dashboard/
│       └── index.html               # Operator dashboard
├── intake/
│   └── intake.html                  # 9-section client onboarding form
├── website-template-v2/             # Base client site template
│   ├── index.html
│   ├── css/style.css
│   └── js/main.js
├── tests/
│   └── fixtures/
│       └── example_intake.json
├── docs/
│   ├── servicetitan_integration.md
│   └── deploy.md
├── .env.example
├── .gitignore
├── requirements.txt
├── netlify.toml
└── vercel.json
```

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Fill in: OPENAI_API_KEY, TWILIO_*, SENDGRID_API_KEY

# 3. Run backend
uvicorn backend.main:app --reload --port 8000

# 4. Build a client site
python builder/site_generator.py --intake tests/fixtures/example_intake.json

# 5. Open dashboard
open http://localhost:8000/dashboard
open http://localhost:8000/docs
```

---

## Testing Agent Actions

```bash
# Simulate missed call
curl -X POST http://localhost:8000/webhooks/voice/incoming \
  -d "To=+16025550192&From=+16025559999"

# Simulate lead form
curl -X POST http://localhost:8000/webhooks/lead-form \
  -H "Content-Type: application/json" \
  -d '{"client_id":"CLIENT_ID","name":"John Smith","phone":"+16025559876","message":"AC not cooling"}'

# Simulate job complete → review request
curl -X POST http://localhost:8000/webhooks/job-complete \
  -H "Content-Type: application/json" \
  -d '{"client_id":"CLIENT_ID","customer_phone":"+16025559876","customer_name":"John Smith","job_type":"AC Repair","google_review_link":"https://g.page/r/your-link"}'
```

---

## Deployment

See `docs/deploy.md` for Railway, Render, and Netlify instructions.

---

## Intake JSON Schema

```json
{
  "biz_name":     "Desert Air HVAC",
  "phone":        "(602) 555-0192",
  "email":        "owner@example.com",
  "industry":     "HVAC",
  "service_area": "Phoenix, AZ",
  "tagline":      "Same-day HVAC service guaranteed.",
  "plan":         "growth",
  "rating_value": 4.9,
  "review_count": 214,
  "services":     ["AC Repair", "AC Install", "Furnace Repair", "Duct Cleaning"]
}
```

**Industries:** `Contractor` | `HVAC` | `Plumber` | `Electrician` | `Roofing` | `Restaurant` | `Med Spa` | `Dentist` | `Other`  
**Plans:** `essentials` | `growth` | `pro`

---

## Adding a New AI Employee

1. Add the agent file to `backend/agents/`
2. Add the route trigger to `backend/routes/webhooks.py`
3. Add the staff card to `website-template-v2/index.html` and `intake/intake.html`

That's it — the new employee appears in intake previews, generated sites, and the dashboard.
