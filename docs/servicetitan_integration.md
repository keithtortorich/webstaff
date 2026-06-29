# ServiceTitan Integration — Technical Specification
**WebStaffr · Version 1.0 · June 2026**

---

## Strategic Positioning

WebStaffr is the front-office layer that feeds ServiceTitan. We do not compete with the platform; we increase its ROI by ensuring no lead is missed before it reaches the dispatcher's board.

**Positioning line:** *"Keep ServiceTitan for field operations. Use WebStaffr for the front office that feeds it."*

ServiceTitan owns scheduling, dispatch, invoicing, and customer records. WebStaffr owns every customer interaction that happens before a job is created — the call, the form, the follow-up, the booking, the review request after the job closes.

---

## Investor Reframe

**Expected question:** "What happens when ServiceTitan builds this?"

**Answer:** We want them to. It validates the category. It confirms that every contractor needs AI running the front office. And because WebStaffr is already integrated into their platform — and listed in their Marketplace — we benefit from their distribution rather than compete against it.

The competitive moat is not "ServiceTitan won't build this." It is:

1. **Specialization beats breadth** — a front-office AI built only for that purpose outperforms a feature bolted onto an FSM
2. **First-mover in the install base** — WebStaffr clients who integrated first are sticky; switching to an ST-native solution requires active work to undo
3. **Marketplace positioning** — as a listed partner, WebStaffr benefits from ST's co-marketing, not competes against it
4. **Trade extension** — ST focuses on HVAC, plumbing, electrical; WebStaffr expands to restaurants, med spas, dental, and trades ST does not serve

---

## Integration Roadmap

| Phase | Timeline | Mechanism | ST Credentials Required |
|---|---|---|---|
| **Phase 1 — Zapier Bridge** | Active (MVP) | Webhook → Zapier → ST API | No |
| **Phase 2 — Native OAuth API** | Weeks 4–8 | Direct ST V2 REST API, OAuth 2.0 | Yes |
| **Phase 3 — AI Context Layer** | Months 2–4 | Pull ST history into AI system prompt | Yes |
| **Phase 4 — ST Marketplace** | Months 3–6 | Silver-tier App Marketplace listing | Partner program |

---

## Phase 1: Zapier Bridge (Active)

No ServiceTitan credentials required. Setup time: 5 minutes per client.

### Setup Steps

1. Log into [Zapier](https://zapier.com) → **New Zap**
2. Trigger: **Webhooks by Zapier** → **Catch Hook** → copy the generated webhook URL
3. Paste URL into WebStaffr `.env` as `ZAPIER_SERVICETITAN_WEBHOOK_URL`
4. Action 1: **ServiceTitan** → **Create or Update Customer** — map fields from payload below
5. Action 2: **ServiceTitan** → **Create Job** — map `job_type`, `job_notes`, `job_source = "WebStaffr"`
6. Activate the Zap

Every new WebStaffr lead now auto-creates an ST customer and job before the contractor reads their own notification.

### Payload Sent to Zapier

The following JSON is posted by `backend/routes/integrations.py` → `_zapier_sync()`:

```json
{
  "customer_name":       "John Smith",
  "customer_phone":      "+16025550192",
  "customer_email":      "john@example.com",
  "customer_message":    "AC not cooling — need same day",
  "job_type":            "HVAC",
  "job_source":          "WebStaffr",
  "job_notes":           "AI-captured lead. Source: form. Lead ID: uuid-...",
  "business_unit":       "Desert Air HVAC",
  "service_area":        "Phoenix, AZ",
  "webstaffr_lead_id":   "uuid-...",
  "webstaffr_client_id": "uuid-...",
  "platform":            "servicetitan"
}
```

Map `customer_name`, `customer_phone`, `customer_email` to the ST Customer fields. Map `job_type` to Business Unit, `job_source` to Lead Source, `job_notes` to the Job Summary.

---

## Phase 2: Native OAuth API (Weeks 4–8)

### Authentication

ServiceTitan uses OAuth 2.0 Client Credentials flow.

```
POST https://auth.servicetitan.io/connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={ST_CLIENT_ID}
&client_secret={ST_CLIENT_SECRET}
```

Tokens are short-lived and refreshed per request. Never stored at rest.

Required `.env` variables: `ST_CLIENT_ID`, `ST_CLIENT_SECRET`, `ST_TENANT_ID`

Sandbox access: [developer.servicetitan.io](https://developer.servicetitan.io)

The integration code in `backend/routes/integrations.py` detects native credentials automatically. When `ST_CLIENT_ID` and `ST_CLIENT_SECRET` are set, it routes through `_st_native_sync()`; otherwise it falls back to the Zapier bridge.

### Deduplication

Before creating a new customer, the integration searches ST by phone number:

```
GET /crm/v2/tenant/{id}/customers?phoneNumber={phone}
```

If a match is found, the existing record is updated (`PATCH`) rather than duplicated.

### Bidirectional Event Table

| ST Event | WebStaffr Action |
|---|---|
| Customer created | Lead status → `contacted`, `servicetitan_customer_id` stored |
| Job created | Lead status → `booked`, `servicetitan_job_id` stored |
| Tech dispatched | (Phase 3) website job tracker updated |
| Job complete | Reputation Manager fires → review request SMS |
| Invoice paid | Revenue event logged for LTV tracking |

### Key API Endpoints

| Action | Method | Endpoint |
|---|---|---|
| Search customer | GET | `/crm/v2/tenant/{id}/customers?phoneNumber=` |
| Create customer | POST | `/crm/v2/tenant/{id}/customers` |
| Update customer | PATCH | `/crm/v2/tenant/{id}/customers/{customerId}` |
| Create job | POST | `/jpm/v2/tenant/{id}/jobs` |
| Get job status | GET | `/jpm/v2/tenant/{id}/jobs/{jobId}` |

---

## Phase 3: AI Context Layer (Months 2–4)

Before each AI Receptionist conversation, WebStaffr pulls the caller's history from ServiceTitan and injects it into the system prompt.

### Fields Retrieved

- Customer name, address, membership status
- Last 3 jobs: type, date, technician, status
- Installed equipment: model, serial, age, warranty expiry
- Outstanding invoices or open follow-ups

### Prompt Injection

`backend/routes/integrations.py` → `build_context_prompt()` converts the retrieved context into a natural-language injection:

```
This is a RETURNING CUSTOMER. Their name is Mike.
They have an active Gold Membership.
Most recent job: AC Repair (completed, 2025-06-14).
Reference their history naturally — make them feel recognized.
Example: "Welcome back, Mike. I see we serviced your AC last June — what can we do for you today?"
```

### Example Conversation Enabled by Phase 3

> *"Hi, you've reached Desert Air HVAC — this is your AI receptionist. Welcome back, Mike. I see we replaced your condenser last summer and you're still under our two-year parts warranty. Are you calling about a warranty issue, or something new?"*

This is not a feature. It is the difference between a generic answering service and a front-office employee who actually knows the customer.

---

## Phase 4: ServiceTitan App Marketplace (Months 3–6)

**Target tier:** Silver (minimum viable public listing)

**Requirements for Silver listing:**
- Sandbox integration reviewed and approved by ST partner team
- Security review: OAuth lifecycle, PII handling, data retention documentation
- Co-marketing agreement with ST partner team

**Benefits upon listing:**
- Access to ST's contractor install base as a discovery channel
- "Works with ServiceTitan" badge on WebStaffr marketing materials
- Inclusion in ST partner newsletters and co-marketing
- Reduced onboarding friction for existing ST users (one-click install path)

**Timeline:** Submit for review at month 3; target live listing by month 6.

---

## Security

| Control | Implementation |
|---|---|
| OAuth tokens | Short-lived, refreshed per request, never stored at rest |
| PII at rest | Encrypted in database; lead records purged per retention policy |
| PII in transit | TLS 1.3 on all connections |
| API scopes | Least-privilege — request only what each sync operation requires |
| Webhook verification | Signature validation on all inbound ST webhook events |
| Audit logging | Every sync event logged: timestamp, payload hash, success/failure, lead ID |
| Operator consent | Contractor grants explicit data-sharing consent during WebStaffr onboarding |
| TCPA | SMS sent only to numbers that have called in or submitted a form — never cold outreach |

---

## Future FSM Integrations

The integration layer in `backend/routes/integrations.py` is platform-agnostic. `detect_fsm()` routes each client to the correct platform; `_zapier_sync()` handles Phase 1 for all platforms using the same payload schema.

| Platform | Type | Priority | Timeline | Architecture |
|---|---|---|---|---|
| **Jobber** | FSM — smaller contractors | High | Phase 2 (weeks 4–8) | Zapier bridge live; native GraphQL API stubbed |
| **Housecall Pro** | FSM — mid-market | High | Phase 2 (weeks 4–8) | Zapier bridge live; REST API stubbed |
| **FieldPulse** | FSM — growing segment | Medium | Phase 3 (months 2–4) | Same Zapier pattern; native TBD |
| **Service Fusion** | FSM — legacy base | Medium | Phase 3 | Zapier bridge sufficient |
| **Workiz** | FSM — specialty trades | Medium | Phase 3 | Zapier bridge sufficient |
| **Google Calendar** | Scheduling (no FSM) | High | Phase 2 | Direct Google Calendar API |
| **QuickBooks** | Accounting | Low | Phase 4 | Future revenue line |

Adding a new FSM requires: one Zapier Zap + one `.env` variable + one `detect_fsm()` branch. The core sync logic is already written and reused.

---

*WebStaffr · Confidential · K. Michael Tortorich, MD (CEO) · Patrick Bukowski (COO) · Wenjie Tong (CTO)*
