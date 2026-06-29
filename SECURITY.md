# Security Policy

## Supported Versions

WebStaffr is currently in MVP release. Only the current version in the `main`
branch receives security fixes. Prior commits are not maintained.

| Version | Supported |
|---|---|
| `main` (current) | ✅ Yes |
| Any prior commit | ❌ No |

---

## Reporting a Vulnerability

**Email:** security@webstaffr.com

**Response SLA:**
- Acknowledgment within 24 hours
- Initial assessment within 72 hours
- Fix timeline communicated within 5 business days

Please include:
- Description of the vulnerability and potential impact
- Steps to reproduce
- Any proof-of-concept code (do not post publicly)

We do not operate a bug bounty program at this stage. All responsible
disclosures are acknowledged in release notes.

---

## In-Scope

The following are in scope for security review:

**API endpoints**
- All routes under `/webhooks/` — webhook authentication and request validation
- All routes under `/api/` — authorization, input validation, rate limiting
- The `/api/onboard` endpoint — intake payload injection risks

**Webhook authentication**
- Twilio webhook signature validation (HMAC-SHA1 on `X-Twilio-Signature`)
- Inbound ServiceTitan webhook signature verification
- Missing or bypassable signature validation on any inbound route

**PII handling**
- Lead records: name, phone, email, message stored in DB
- Agent event logs: input/output payloads may contain caller phone numbers
- Call recordings or transcripts (future feature) if stored without encryption

**Twilio credential exposure**
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in environment or logs
- Phone number enumeration via webhook routing logic

**Dependency vulnerabilities**
- CVEs in `fastapi`, `sqlalchemy`, `twilio`, `openai`, `sendgrid`, or
  any package in `requirements.txt`

---

## Out of Scope

The following are explicitly out of scope:

- Vulnerabilities in third-party platforms: Twilio, SendGrid, OpenAI, Zapier,
  ServiceTitan, Netlify, Railway, Render
- Social engineering of WebStaffr staff or contractors
- Physical security
- Rate limiting on public demo endpoints during the pre-launch period
- Issues that require physical access to a device

---

## Data Handling

### What WebStaffr stores

| Data | Location | Retention |
|---|---|---|
| Lead records (name, phone, email, message) | `leads` table | Retained until client requests deletion |
| Agent event logs (input/output payloads) | `agent_events` table | 90 days rolling |
| Review requests (customer phone, sent timestamp) | `review_requests` table | 12 months |
| Client records (biz name, phone, email, plan) | `clients` table | Retained for billing and audit |

### Encryption

- All data in transit: TLS 1.3
- Database at rest: encrypted at the infrastructure level (Railway/Render managed)
- PII fields (phone, email) are not additionally encrypted at the application
  layer in MVP; field-level encryption is on the Phase 2 security roadmap

### Deletion requests

Contractors can request deletion of their client record and all associated
leads and agent events by emailing support@webstaffr.com. Deletion is
processed within 30 days.

---

## TCPA Compliance

WebStaffr sends SMS only in the following circumstances:

1. **Missed call text-back** — the caller initiated contact by calling the
   contractor's number. The SMS is a direct response to that inbound call.
2. **Lead form follow-up** — the homeowner submitted a contact form on the
   contractor's website. The SMS is a response to that submission.
3. **Post-job review request** — triggered by the contractor marking a job
   complete for a customer who previously engaged with their business.

**WebStaffr never sends cold SMS.** No SMS is sent to any number that has
not first called in or submitted a form. The Zapier lead-gen pipeline
(`docs/servicetitan_integration.md`) and any prospecting tools in the repo
are for outreach research only — they do not trigger any automated SMS sends.

Operators are responsible for ensuring their own TCPA compliance,
particularly regarding opt-out handling and DNC registry scrubbing for
any manual outreach they conduct outside the WebStaffr platform.

---

## Credential Hygiene — Operator Checklist

Operators running WebStaffr are responsible for the following:

```
[ ] Never commit .env to git — it is in .gitignore, keep it there
[ ] Rotate OPENAI_API_KEY if any team member with access departs
[ ] Rotate TWILIO_AUTH_TOKEN immediately if it appears in any log or chat
[ ] Rotate SENDGRID_API_KEY on any suspected exposure
[ ] Use Railway / Render environment variable UI — never paste keys into
    source code or config files that are tracked by git
[ ] Revoke and regenerate all keys after any security incident
[ ] Do not share .env files over email or Slack — use a secrets manager
    (Railway's built-in env vars, Doppler, or 1Password Secrets Automation)
[ ] GitHub PATs used for repo access should be scoped to minimum permissions
    and rotated after every use in a CI/CD context
[ ] Audit active Zapier Zaps quarterly — revoke any that are no longer in use
```

**If you believe a key has been exposed:** rotate it immediately at the
provider (OpenAI, Twilio, SendGrid), redeploy with the new key, and email
security@webstaffr.com with the details.

---

## Known Limitations (MVP)

The following are known security limitations acknowledged for the MVP stage:

- **No dashboard authentication** — the operator dashboard at `/dashboard`
  is unauthenticated. Do not expose the backend URL publicly until dashboard
  auth is added (on the Phase 2 roadmap).
- **SQLite in development** — SQLite does not support row-level encryption.
  Use Postgres in production via `DATABASE_URL`.
- **CORS is open** (`allow_origins=["*"]` in `backend/main.py`) — tighten
  to your specific Netlify domain before production launch.
- **No rate limiting** on webhook endpoints — a malicious actor with your
  Twilio webhook URL could spam the `/webhooks/voice/incoming` endpoint.
  Add rate limiting before public launch.
