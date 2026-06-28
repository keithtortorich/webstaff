# WebStaff — AI Workforce for Home Service Businesses

> *We run the office while contractors run the business.*

WebStaff builds client websites and deploys a named AI workforce — Receptionist, Lead Coordinator, Reputation Manager, and more — based on the client's chosen plan. The website is free. Clients invest in the AI staff that makes it produce revenue.

---

## Project Structure

```
webstaff/
├── intake/
│   └── intake.html              # Client onboarding form (auto-submits to build API)
├── api/
│   └── build.py                 # Flask API: receives intake JSON → triggers build
├── builder/
│   └── site_generator.py        # Core site generator (run directly or via API)
├── website-template-v2/
│   └── index.html               # Base HTML template with {{placeholders}}
├── clients/                     # Output: generated client sites (gitignored)
├── tests/
│   └── fixtures/
│       └── example_intake.json  # Example intake for CI + local testing
├── github_workflows/            # Copy contents to .github/workflows/
│   ├── build.yml                # CI: validate + build on push
│   └── deploy.yml               # CD: deploy to Netlify or Vercel
├── netlify.toml
├── vercel.json
└── requirements.txt
```

> **Note:** Rename `github_workflows/` to `.github/workflows/` in your repo.

---

## Workforce Plans

| Plan | Price | AI Staff Deployed |
|---|---|---|
| **Essentials** | $197/mo | Website Operations Manager |
| **Growth** *(recommended)* | $497/mo | + Receptionist, Lead Coordinator, Reputation Manager, Sales Consultant |
| **Pro** | $997/mo | + Marketing Coordinator, Growth Manager, Service Advisor |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Build a site from an intake file

```bash
python3 builder/site_generator.py --intake tests/fixtures/example_intake.json
```

Output is written to `clients/<biz_slug>_<date>/`.

### 3. Validate intake without building

```bash
python3 builder/site_generator.py --intake my_client.json --validate
```

### 4. Run the build API locally

```bash
python3 api/build.py
# API runs at http://localhost:5050
```

Then open `intake/intake.html` in a browser. The form auto-submits to `http://localhost:5050/api/build`.

---

## Intake JSON Schema

```json
{
  "biz_name":     "Apex Plumbing LLC",       // required
  "phone":        "(512) 555-0192",           // required
  "email":        "owner@example.com",
  "industry":     "Plumber",                  // required: Contractor | Plumber | Dentist | Med Spa | Restaurant | Other
  "service_area": "Austin, TX",               // required
  "site_url":     "https://example.com",
  "tagline":      "Fast, reliable plumbing.", 
  "plan":         "growth",                   // required: essentials | growth | pro
  "rating_value": 4.9,                        // optional — only include if real
  "review_count": 138                         // optional — only include if real
}
```

---

## Deployment

### Netlify

1. Add secrets to Netlify: `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`
2. Set environment variable `INTAKE_FILE` per site to the path of your intake JSON
3. Push to `main` — GitHub Actions deploys automatically

### Vercel

1. Add secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
2. Set `INTAKE_FILE` in Vercel project settings
3. Push to `main` — auto-deploy via GitHub Actions

### Manual deploy trigger

Use the `workflow_dispatch` trigger in GitHub Actions to deploy any intake file to either platform on demand.

---

## GitHub Actions Secrets Required

| Secret | Used by |
|---|---|
| `NETLIFY_AUTH_TOKEN` | deploy.yml → Netlify |
| `NETLIFY_SITE_ID` | deploy.yml → Netlify |
| `VERCEL_TOKEN` | deploy.yml → Vercel |
| `VERCEL_ORG_ID` | deploy.yml → Vercel |
| `VERCEL_PROJECT_ID` | deploy.yml → Vercel |

---

## AI Workforce Widget

The generated site includes an interactive workforce panel that:

- Shows all possible AI staff roles organized by department (Front Office, Marketing, Sales, Operations)
- Highlights which roles are **active** on the client's plan
- Grays out roles not included (showing upgrade potential)
- Fires a toast notification from the Receptionist on Growth/Pro plans
- Uses `IntersectionObserver` to render on scroll for performance

The active features are embedded by the builder into a `data-features` attribute read by the site's JS — no backend call required at runtime.

---

## Adding a New AI Employee

1. Add the role to `WORKFORCE_BY_PLAN` in `builder/site_generator.py`
2. Add the matching entry to `ALL_STAFF` in `website-template-v2/index.html`
3. Add the chip to `WORKFORCE` in `intake/intake.html`

That's it — the new role automatically appears in intake previews, generated sites, and build manifests.
