WebStaff Lead-Gen Pipeline — Build Spec
US Home-Service Trades | v1.0 | 2026-06-27
Owners: Keith (strategy, targeting, copy, calls) · Adam (scrape/audit/enrich automation, sending infra)


How to read this doc
Confidence legend (per line): ✅ verified against current public sources · 🔵 [Inference] our reasoning · ⚪ [Unverified] vendor/marketing claim, treat as directional

Flags: ⛓️ hard dependency · ⏱️ lead-time prerequisite (start early)

This doc mixes verified facts and inferences; each item is labeled. Compliance notes are 🔵 [Inference] from current sources, not legal advice — confirm with counsel before any cold outreach deploys.


1. Objective
Produce a repeatable system that converts a target trade + metro into a scored, contactable prospect list, then runs compliant cold outreach with the website audit as the pitch. Output funnels into the existing WebStaff intake-form → auto-SMS loop → 3-round gap-fill handoff.

Success criterion (v1): One trade × one metro fully processed end-to-end, first cold-email sequence live, ≥1 booked call. 🔵


2. Architecture (data flow)
STAGE 0  Targeting (vertical × zip list)

            │

STAGE 1  Scrape Google Maps (ALL listings, keep website field)

            │

            ├── website BLANK ──► SEGMENT A (no-site)

            │                          │ (skip audit)

            └── website PRESENT ─► SEGMENT B (has-site)

                                       │

STAGE 2                          Audit site (PageSpeed/Lighthouse) → score + findings

                                       │

            ┌──────────────────────────┘

            ▼

STAGE 3  Enrich + validate email (fallback: phone)

            │

STAGE 4  Cold outreach

            ├── email-capable ──► CAN-SPAM email sequence (3 touches)

            └── email-missing ──► manual phone call

            │

STAGE 5  Reply/interest ──► manual call ──► intake form ──► [EXISTING auto-SMS loop]

Parallel track (start day 1): ⏱️ Sending-domain purchase + warmup (2–4 wks) runs alongside Stages 0–3.


3. Stage specs
Stage 0 — Targeting ⛓️ prerequisite for all
Field
Spec
Purpose
Define scope; build zip list to beat the per-query cap
Owner
Keith
Action
Pick 1 trade × 1 metro (e.g. HVAC × Phoenix). Generate full zip-code list for metro.
Why zips
Google returns ~500 places max per query ✅ — one citywide query under-collects in dense US metros 🔵
Output
CSV: vertical, city, state, zip (one row per query)
Done when
Query-row CSV exists and is handed to Adam

Stage 1 — Scrape ⛓️ feeds everything
Field
Spec
Purpose
Pull every listing; do NOT pre-filter no-website
Owner
Adam
Tool
Outscraper or Apify Google Maps scraper ✅
Cost
~$2–4 per 1K leads ✅
Output fields
business_name, category, address, city, state, zip, phone, gbp_url, rating, review_count, website_url(nullable)
Derived field
segment = A if website_url blank, else B 🔵
Caveat
Blank website field ≠ no site (some have unlinked site or FB-only) ✅ → Stage 1.5 verify
Done when
Deduped master CSV with segment populated

Stage 1.5 — Verify no-site (Segment A only) 🔵
Quick automated check: search business_name + city; if a real site surfaces, reclassify B or drop. 🔵
Owner: Adam (scriptable) · Done when: Segment A false-positives removed.
Stage 2 — Audit (Segment B only) ⛓️ needs Stage 1 URLs
Field
Spec
Purpose
Generate the score + specific findings that become the pitch
Owner
Adam
Free tier
Google PageSpeed Insights API — free ✅ → mobile score, Core Web Vitals, full Lighthouse
Signal layer
BuiltWith/Wappalyzer ⚪ → flags: no SSL, dead/old CMS, not mobile-responsive
Optional depth
DataForSEO On-Page: $0.000125/page, $50 min, pay-as-you-go ✅ (60+ metrics, Lighthouse)
Rate limits
PageSpeed API: respect Google quota; batch with backoff 🔵
Output
audit_score (0–100), audit_findings = 2–3 named issues (e.g. "9.2s mobile load", "no SSL", "not mobile-responsive")
Done when
Every Segment B row has score + ≥2 findings

Stage 3 — Enrich + validate ⛓️ gates Stage 4 volume
Field
Spec
Purpose
Get a deliverable email; validate to protect domain reputation
Owner
Adam
Email find
Outscraper/Apify email scraper (crawls /contact, /about) ✅
Validate
Any email-verification service → tag email_status (valid/risky/invalid) 🔵
Fallback
Segment A often emailless → set outreach_channel = phone 🔵
Output
email, email_status, outreach_channel
Done when
Each lead has a routable channel (email valid OR phone present)

Stage 4 — Cold outreach ⏱️ blocked by domain warmup
Field
Spec
Purpose
Run compliant cold sequences; route by channel
Owner
Keith (copy) + Adam (infra)
Email infra
Instantly / Smartlead-type tool w/ inbox rotation + warmup 🔵
Email basis
CAN-SPAM permits cold commercial email w/o prior consent ✅
Phone
Manual calls for emailless leads; trades owners answer in business hours ⚪
Done when
Both sequences live; daily send cadence stable


Email sequence (3 touches):

T+0 — Personalized: name business + one audit finding + link to their report (link, don't attach — deliverability 🔵). Segment A variant = "invisible in search / no site"; Segment B variant = "your site has [specific issue]".
T+3d — Value / social proof.
T+7d — Break-up.
Stage 5 — Handoff to existing system ⛓️
Reply/interest → Keith manual call.
Prospect opts in via intake form → existing auto-SMS loop + 3-round gap-fill (day 1/3/7) takes over.
Rule: cold-list phone numbers meet SMS automation ONLY after this opt-in. 🔵


4. Lead record schema (carries through all stages)
lead_id              uuid

business_name        str

category             str

address/city/state/zip

phone                str

gbp_url              str

rating               float

review_count         int

website_url          str | null

segment              "A" | "B"          (derived, Stage 1)

audit_score          int | null         (Stage 2, B only)

audit_findings       [str] | null       (Stage 2, B only)

email                str | null         (Stage 3)

email_status         "valid"|"risky"|"invalid"|null

outreach_channel     "email" | "phone"  (Stage 3)

sequence_status      enum               (Stage 4)

last_contacted       datetime

outcome              enum               (Stage 5)


5. Compliance guardrails 🔵 [Inference — not legal advice]
Channel
Rule
Source
Cold SMS to scraped lists
Do not. TCPA applies to texts to mobile numbers regardless of B2B context; marketing texts need prior express written consent; $500–$1,500/msg, no cap, private right of action ✅
TCPA
Email (cold)
Allowed: honest headers, commercial-message ID, physical address in footer, working opt-out ✅
CAN-SPAM
SMS (post-opt-in only)
Reserve for prospects who gave their number via intake form 🔵
—
Before ANY SMS send
Check FCC Reassigned Numbers Database → "no" gives a safe-harbor defense ✅
TCPA
SMS infra
10DLC registration governs carrier delivery of A2P traffic ✅
CTIA/10DLC
SMS timing/content
Quiet hours 8am–9pm local; honor STOP; no SHAFT content ✅
CTIA
Regional note
5th Cir (TX/LA/MS): Bradford v. Sovereign Pest (Feb 2026) — oral consent may suffice there; FCC one-to-one rule vacated by 11th Cir ✅. Landscape shifting → don't build a cold-SMS engine on it 🔵
case law



6. Critical path & sequencing ⏱️
Day 1 ──┬── START domain warmup (2–4 wks) ───────────────────────┐

        └── Stage 0 targeting                                     │

Days 2–7 ── Stages 1 → 1.5 → 2 → 3 (list ready, sequences drafted)│

Week 3–4 ── domain warm ─────────────────────────────────────────┴── Stage 4 SEND

Bottleneck = domain warmup, longer than all data work combined. Start it on day 1 in parallel. 🔵


7. Cost to first campaign (1 metro, ~1K leads) 🔵
Item
Est.
Scrape 1K
$2–4 ✅
PageSpeed audit
$0 ✅
Email enrich + validate
~$10–30 ⚪
Cold-email tool (monthly)
~$30–100 ⚪
Sending domain
~$10–15 ✅
Total to launch
~$50–150 🔵



8. Tactical vs strategic split


Tactical (this week)
Strategic (full system)
Scope
Segment A only
Segment A + B + audit engine
Channel
Phone only
Email engine + phone
Setup
None
Domain warmup + tooling
Wait
Zero
2–4 wks (warmup)
Payoff
Fastest revenue
Compounds, scriptable, Adam-ownable


🔵 Recommendation: run tactical (Segment A phone) for cash flow while the strategic email engine warms up. They don't compete.
