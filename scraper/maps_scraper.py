#!/usr/bin/env python3
"""
WebStaff Lead Scraper — Phoenix HVAC Beachhead
Wraps Outscraper via CSV simulation for local dev; swap generate_mock_leads()
for a real Outscraper API call in production.

Usage:
  python3 scraper/maps_scraper.py --trade hvac --city "Phoenix, AZ" --zips zips.csv
  python3 scraper/maps_scraper.py --trade hvac --city "Phoenix, AZ" --max 50 --output leads.csv
"""

import json, csv, time, argparse, sys, re

# ── Trade definitions ──────────────────────────────────────────────────────────
TRADES = {
    "hvac": {
        "terms": [
            "HVAC contractor", "AC repair", "air conditioning repair",
            "heating and cooling", "air conditioner installation",
            "furnace repair", "heat pump installation", "HVAC service",
        ],
        "label": "HVAC",
        "avg_ticket": "$400-$12,000",
        "webstaff_pitch": "Never lose a call when the AC dies at midnight.",
    },
    "plumbing": {
        "terms": [
            "plumber", "plumbing contractor", "drain cleaning",
            "water heater repair", "water heater installation",
            "emergency plumber", "pipe repair",
        ],
        "label": "Plumbing",
        "avg_ticket": "$300-$8,000",
        "webstaff_pitch": "Water emergencies don't wait — your AI Receptionist shouldn't either.",
    },
    "roofing": {
        "terms": [
            "roofing contractor", "roof repair", "roof replacement",
            "roofer", "storm damage roof", "shingle roof",
        ],
        "label": "Roofing",
        "avg_ticket": "$5,000-$20,000",
        "webstaff_pitch": "Insurance leads go to whoever responds first — be first.",
    },
    "electrical": {
        "terms": [
            "electrician", "electrical contractor", "electrical repair",
            "panel upgrade", "EV charger installation",
        ],
        "label": "Electrical",
        "avg_ticket": "$300-$5,000",
        "webstaff_pitch": "Electrical emergencies drive high-value calls — don't miss them.",
    },
}

# Phoenix metro zip codes (partial list for beachhead)
PHOENIX_ZIPS = [
    "85001","85002","85003","85004","85006","85007","85008","85009",
    "85012","85013","85014","85015","85016","85017","85018","85019",
    "85020","85021","85022","85023","85024","85025","85027","85028",
    "85029","85031","85032","85033","85034","85035","85040","85041",
    "85042","85043","85044","85045","85048","85050","85051","85053",
    "85054","85083","85085","85086","85087","85201","85202","85203",
    "85204","85205","85206","85207","85208","85209","85210","85212",
    "85213","85215","85224","85225","85226","85233","85234","85248",
    "85249","85250","85251","85253","85254","85255","85257","85258",
    "85259","85260","85262","85266","85281","85282","85283","85284",
    "85301","85302","85303","85304","85305","85306","85307","85308",
    "85309","85310","85318","85323","85338","85339","85340","85345",
    "85351","85353","85374","85375","85379","85381","85382","85383",
    "85388","85395",
]

# ── Mock lead generation (replace with Outscraper API in production) ──────────
def generate_leads(trade_key: str, config: dict, city: str, max_results: int = 50) -> list[dict]:
    """
    In production: call Outscraper Google Maps API here.
    https://outscraper.com/google-maps-scraper/
    Cost: ~$2-4 per 1K results.

    For dev/demo, returns synthetic records with the same schema.
    """
    results = []
    city_name = city.split(",")[0].strip()
    state     = city.split(",")[1].strip() if "," in city else ""

    for i in range(1, max_results + 1):
        term = config["terms"][i % len(config["terms"])]
        # Simulate ~45% no-website rate (per business plan — trades highest category)
        has_website = (i % 10) >= 4   # ~60% have website for this mock
        website_url = f"https://{city_name.lower().replace(' ','-')}-hvac-{i}.com" if has_website else ""

        results.append({
            "lead_id":      f"{trade_key}-{city_name.lower().replace(' ','')}-{i:04d}",
            "business_name":f"{city_name} {term.title()} #{i}",
            "category":     config["label"],
            "address":      f"{100+i} Main St, {city}",
            "city":         city_name,
            "state":        state,
            "zip":          PHOENIX_ZIPS[i % len(PHOENIX_ZIPS)],
            "phone":        f"(602) 5{i:02d}-{i:04d}",
            "gbp_url":      f"https://g.page/{city_name.lower()}-hvac-{i}",
            "rating":       f"{4.0 + (i % 8) * 0.1:.1f}",
            "review_count": str(15 + i * 7),
            "website_url":  website_url,
            "segment":      "A" if not website_url else "B",  # A=no-site, B=has-site
            "avg_ticket":   config["avg_ticket"],
            "scraped_at":   time.strftime("%Y-%m-%d %H:%M:%S"),
            # B-segment fields (populated in Stage 2 audit):
            "audit_score":  "",
            "audit_findings": "",
            # Stage 3 email enrichment fields:
            "email":        "",
            "email_status": "",
            "outreach_channel": "",
            # Stage 4/5 tracking:
            "sequence_status": "new",
            "last_contacted": "",
            "outcome":      "",
        })

    return results

def main():
    p = argparse.ArgumentParser(description="WebStaff Lead Scraper — Phoenix HVAC Beachhead")
    p.add_argument("--trade", "-t", default="hvac",
                   choices=list(TRADES.keys()),
                   help="Trade vertical to target")
    p.add_argument("--city", "-c", default="Phoenix, AZ",
                   help="City to target (e.g. 'Phoenix, AZ')")
    p.add_argument("--max", "-m", type=int, default=50,
                   help="Max leads per query")
    p.add_argument("--zips", help="CSV file with zip codes (one per row, first column)")
    p.add_argument("--output", "-o", help="Write results to CSV file")
    p.add_argument("--segment", choices=["A","B","all"], default="all",
                   help="Filter: A=no-website, B=has-website, all=both")
    args = p.parse_args()

    config = TRADES[args.trade]

    # Load zip list (for production: run one query per zip to beat 500/query cap)
    zips = []
    if args.zips:
        with open(args.zips) as f:
            zips = [row[0].strip() for row in csv.reader(f) if row]
        print(f"Loaded {len(zips)} zip codes from {args.zips}", file=sys.stderr)
    else:
        zips = [args.city]  # Dev: single city query

    all_results = []
    for query_target in zips[:5]:  # Cap at 5 for demo; remove cap in production
        results = generate_leads(args.trade, config, query_target if "," in query_target else args.city, args.max)
        all_results.extend(results)

    # Deduplicate by business_name + phone
    seen = set()
    deduped = []
    for r in all_results:
        key = (r["business_name"], r["phone"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Filter by segment
    if args.segment != "all":
        deduped = [r for r in deduped if r["segment"] == args.segment]

    seg_a = sum(1 for r in deduped if r["segment"] == "A")
    seg_b = sum(1 for r in deduped if r["segment"] == "B")

    print(f"\nWebStaff Lead Scraper — {config['label']} × {args.city}", file=sys.stderr)
    print(f"{'='*55}", file=sys.stderr)
    print(f"  Total leads:  {len(deduped):,}", file=sys.stderr)
    print(f"  Segment A (no website):  {seg_a:,}  ← free-site pitch", file=sys.stderr)
    print(f"  Segment B (has website): {seg_b:,}  ← audit pitch", file=sys.stderr)
    print(f"  Avg ticket:  {config['avg_ticket']}", file=sys.stderr)
    print(f"  Pitch angle: {config['webstaff_pitch']}", file=sys.stderr)
    print(f"\nCompliance reminder:", file=sys.stderr)
    print(f"  ✅ Cold email (CAN-SPAM) — primary channel", file=sys.stderr)
    print(f"  ✅ Phone calls — manual only", file=sys.stderr)
    print(f"  ❌ Cold SMS to scraped numbers — TCPA violation risk, do NOT use", file=sys.stderr)
    print(f"  ✅ SMS only after opt-in via intake form\n", file=sys.stderr)

    fields = [
        "lead_id","business_name","category","address","city","state","zip",
        "phone","gbp_url","rating","review_count","website_url","segment",
        "avg_ticket","audit_score","audit_findings","email","email_status",
        "outreach_channel","sequence_status","last_contacted","outcome","scraped_at",
    ]

    if args.output:
        with open(args.output, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(deduped)
        print(f"Saved {len(deduped)} leads → {args.output}", file=sys.stderr)
    else:
        print(json.dumps(deduped[:5], indent=2))
        if len(deduped) > 5:
            print(f"\n... and {len(deduped)-5} more. Use --output to save all.", file=sys.stderr)

if __name__ == "__main__":
    main()
