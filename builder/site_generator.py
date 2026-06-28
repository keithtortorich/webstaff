#!/usr/bin/env python3
"""
WebStaff Client Site Generator
Produces a complete, investor-ready client website from an intake JSON.
Usage:
  python3 builder/site_generator.py --intake tests/fixtures/example_intake.json
  python3 builder/site_generator.py --intake client.json --validate
"""

import os, shutil, json, argparse, re
from pathlib import Path
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent.parent / "website-template-v2"
OUTPUT_BASE  = Path(__file__).parent.parent / "clients"

# ── Industry presets ──────────────────────────────────────────────────────────
INDUSTRY_PRESETS = {
    "Contractor / Construction": {
        "fonts":   "Oswald:wght@700&family=Inter:wght@400;600",
        "primary": "#1a1a1a", "accent": "#d97706", "vibe": "rugged",
        "type":    "GeneralContractor",
    },
    "Plumbing / HVAC / Electrical": {
        "fonts":   "Archivo+Black:wght@400&family=Inter:wght@400;600",
        "primary": "#1e3a8a", "accent": "#ef4444", "vibe": "urgent",
        "type":    "Plumber",
    },
    "Roofing": {
        "fonts":   "Oswald:wght@700&family=Inter:wght@400;600",
        "primary": "#1a1a1a", "accent": "#d97706", "vibe": "rugged",
        "type":    "RoofingContractor",
    },
    "Medical / Dental / Health": {
        "fonts":   "Outfit:wght@600&family=Inter:wght@400;500",
        "primary": "#0f766e", "accent": "#14b8a6", "vibe": "clean",
        "type":    "MedicalBusiness",
    },
    "MedSpa / Aesthetics": {
        "fonts":   "Cormorant+Garamond:wght@700&family=Inter:wght@400;500",
        "primary": "#4c1d95", "accent": "#c026d3", "vibe": "luxury",
        "type":    "HealthAndBeautyBusiness",
    },
    "Landscaping / Cleaning": {
        "fonts":   "Inter:wght@400;700",
        "primary": "#14532d", "accent": "#16a34a", "vibe": "fresh",
        "type":    "HomeAndConstructionBusiness",
    },
    "Auto Repair / Detailing": {
        "fonts":   "Sora:wght@600&family=Inter:wght@400;500",
        "primary": "#1e1e2e", "accent": "#f59e0b", "vibe": "energetic",
        "type":    "AutoRepair",
    },
    "Other": {
        "fonts":   "Inter:wght@400;600",
        "primary": "#1e40af", "accent": "#3b82f6", "vibe": "modern",
        "type":    "LocalBusiness",
    },
}

# ── Default services by trade ─────────────────────────────────────────────────
DEFAULT_SERVICES = {
    "Plumbing / HVAC / Electrical": [
        ("🌡️", "AC Repair & Replacement",    "Emergency repair and new system installation. Same-day service when your AC fails."),
        ("🔥", "Heating & Furnace",           "Heat pump, furnace, and boiler installation, repair, and tune-ups."),
        ("💧", "Plumbing Services",           "Leak repair, water heater, drain cleaning, and full repiping."),
        ("⚡", "Electrical",                   "Panel upgrades, outlets, EV chargers, and whole-home wiring."),
        ("🛠️", "Maintenance Plans",            "Annual tune-ups and priority service to keep systems running all year."),
        ("🌿", "Indoor Air Quality",           "Air purifiers, humidifiers, UV lights, and duct cleaning."),
    ],
    "Roofing": [
        ("🏠", "Roof Repair",                 "Leaks, missing shingles, storm damage — diagnosed and fixed fast."),
        ("🔨", "Roof Replacement",            "Full tear-off with premium materials and a 10-year workmanship warranty."),
        ("🌧️", "Gutter Installation",         "Seamless gutters and gutter guards that protect your foundation."),
        ("💨", "Storm Damage Repair",         "Insurance claims assistance and emergency tarping, 24/7."),
        ("☀️", "Skylight Installation",       "Energy-efficient skylights with leak-proof professional flashing."),
        ("🔍", "Roof Inspection",             "Drone inspection with a detailed written report — free with any estimate."),
    ],
    "Contractor / Construction": [
        ("🪟", "Windows & Doors",             "Replacement windows and exterior doors that cut energy bills."),
        ("🏡", "Siding & Exteriors",          "Vinyl, fiber cement, and hardie board — installed right the first time."),
        ("🛁", "Bathroom Remodel",            "Full gut-and-rebuild or targeted upgrades. Fixed-price quotes."),
        ("🍳", "Kitchen Remodel",             "Custom cabinets, countertops, and full kitchen transformations."),
        ("🏗️", "Additions",                   "Room additions, garage conversions, and ADU construction."),
        ("🔧", "Handyman & Repairs",          "No job too small. Licensed, insured, and background-checked."),
    ],
    "Other": [
        ("⭐", "Our Core Service",            "Professional, reliable work delivered on time and on budget."),
        ("🛡️", "Quality Guarantee",           "We stand behind every job with a written satisfaction guarantee."),
        ("📞", "Fast Response",               "Call or text — we reply within the hour, every day of the week."),
    ],
}

# ── WebStaff workforce plan definitions ──────────────────────────────────────
WORKFORCE_BY_PLAN = {
    "essentials": ["Website Operations Manager"],
    "growth": [
        "Website Operations Manager", "Receptionist", "Lead Coordinator",
        "Reputation Manager", "Sales Consultant",
    ],
    "pro": [
        "Website Operations Manager", "Receptionist", "Lead Coordinator",
        "Reputation Manager", "Sales Consultant",
        "Marketing Coordinator", "Growth Manager", "Service Advisor",
    ],
}

ALL_STAFF = [
    {"name": "Receptionist",              "dept": "Front Office",  "desc": "Answers every call, 24/7"},
    {"name": "Lead Coordinator",          "dept": "Front Office",  "desc": "Replies in seconds, keeps leads warm"},
    {"name": "Appointment Scheduler",     "dept": "Front Office",  "desc": "Books jobs while you're on the roof"},
    {"name": "Reputation Manager",        "dept": "Marketing",     "desc": "Earns 5-star reviews on autopilot"},
    {"name": "Marketing Coordinator",     "dept": "Marketing",     "desc": "Keeps the business visible every day"},
    {"name": "Growth Manager",            "dept": "Marketing",     "desc": "Brings homeowners from Google & AI search"},
    {"name": "Service Advisor",           "dept": "Sales",         "desc": "Pre-qualifies calls before trucks roll"},
    {"name": "Sales Consultant",          "dept": "Sales",         "desc": "Helps customers say yes to bigger jobs"},
    {"name": "Website Operations Manager","dept": "Operations",    "desc": "Keeps the site live and current, hands-free"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", text.lower().replace(" ", "-").replace("--", "-")).strip("-") or "client"

def city_only(service_area: str) -> str:
    return service_area.split(",")[0].strip()

def phone_clean(phone: str) -> str:
    d = re.sub(r"\D", "", phone)
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) == 10:
        return f"({d[:3]}) {d[3:6]}-{d[6:]}"
    return phone

def phone_digits(phone: str) -> str:
    d = re.sub(r"\D", "", phone)
    return d[1:] if len(d) == 11 and d[0] == "1" else d

# ── SEO / Schema generation ───────────────────────────────────────────────────
def generate_seo_meta(data: dict, preset: dict) -> str:
    city    = city_only(data.get("service_area", "Your City"))
    biz     = data.get("biz_name", "Your Business")
    industry = data.get("industry", "Service")
    phone   = data.get("phone", "(555) 000-0000")
    tagline = data.get("tagline", f"Professional {industry.lower()} services in {city}.")
    title   = f"{industry} in {city} | {biz}"
    desc    = f"{tagline} Fast response, quality work. Call {phone} today."
    return f"""<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">"""

def generate_json_ld(data: dict, preset: dict) -> str:
    city    = city_only(data.get("service_area", "Your City"))
    biz     = data.get("biz_name", "Your Business")
    phone_d = phone_digits(data.get("phone", "5550000000"))
    schema_type = preset.get("type", "LocalBusiness")

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": biz,
        "telephone": f"+1{phone_d}",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressCountry": "US",
        },
        "priceRange": "$$",
    }
    # Only add aggregateRating if real data provided
    rv = data.get("rating_value")
    rc = data.get("review_count")
    if rv and rc:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(rv),
            "reviewCount": str(rc),
            "bestRating": "5",
        }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

# ── Workforce panel HTML ──────────────────────────────────────────────────────
def generate_workforce_panel(plan: str) -> str:
    active = set(WORKFORCE_BY_PLAN.get(plan, WORKFORCE_BY_PLAN["growth"]))
    depts: dict[str, list] = {}
    for s in ALL_STAFF:
        depts.setdefault(s["dept"], []).append(s)

    html = ['<div class="workforce-panel" data-plan="' + plan + '">',
            '<div class="workforce-panel__header">',
            '<span class="workforce-panel__label">Your AI Office Staff</span>',
            f'<span class="workforce-panel__plan">{plan.title()} Plan</span>',
            '</div>']

    for dept, staff_list in depts.items():
        html.append(f'<div class="workforce-dept"><h4 class="workforce-dept__name">{dept}</h4><div class="workforce-dept__staff">')
        for s in staff_list:
            is_active = s["name"] in active
            cls = "workforce-member" + (" workforce-member--active" if is_active else " workforce-member--inactive")
            badge = "✓ Active" if is_active else "Available"
            html.append(
                f'<div class="{cls}">'
                f'<span class="workforce-member__name">{s["name"]}</span>'
                f'<span class="workforce-member__desc">{s["desc"]}</span>'
                f'<span class="workforce-member__badge">{badge}</span>'
                f'</div>'
            )
        html.append('</div></div>')

    html.append('</div>')
    return "\n".join(html)

# ── Service cards ─────────────────────────────────────────────────────────────
def generate_service_cards(data: dict) -> str:
    industry = data.get("industry", "Other")
    services_raw = data.get("services", "")

    # Parse custom services from intake
    custom = [s.strip() for s in services_raw.split("\n") if s.strip()]
    if custom:
        services = [(f"⚙️", s, f"Professional {s.lower()} — quality workmanship, honest pricing.") for s in custom[:6]]
    else:
        services = DEFAULT_SERVICES.get(industry, DEFAULT_SERVICES["Other"])

    delay_classes = ["", " reveal--delay-1", " reveal--delay-2", " reveal--delay-3", " reveal--delay-4", " reveal--delay-4"]
    cards = []
    for i, (icon, title, desc) in enumerate(services[:6]):
        slug = slugify(title)
        cards.append(f"""        <article class="service-card reveal{delay_classes[i]}">
          <div class="service-card__icon" aria-hidden="true">{icon}</div>
          <h3 class="service-card__title">{title}</h3>
          <p class="service-card__desc">{desc}</p>
          <a href="services/{slug}.html" class="service-card__link">{title} in {{{{CITY}}}}</a>
        </article>""")
    return "\n".join(cards)

# ── Select option tags for lead form ─────────────────────────────────────────
def generate_service_options(data: dict) -> str:
    industry = data.get("industry", "Other")
    services_raw = data.get("services", "")
    custom = [s.strip() for s in services_raw.split("\n") if s.strip()]
    if custom:
        items = custom[:6]
    else:
        items = [t for _, t, _ in DEFAULT_SERVICES.get(industry, DEFAULT_SERVICES["Other"])]
    opts = [f'          <option value="{slugify(s)}">{s}</option>' for s in items]
    return "\n".join(opts)

# ── Service page generation ───────────────────────────────────────────────────
def generate_service_pages(data: dict, output_dir: Path):
    industry = data.get("industry", "Other")
    services_raw = data.get("services", "")
    custom = [s.strip() for s in services_raw.split("\n") if s.strip()]
    services = [(slugify(s), s) for s in custom[:6]] if custom else \
               [(slugify(t), t) for _, t, _ in DEFAULT_SERVICES.get(industry, DEFAULT_SERVICES["Other"])]

    biz   = data.get("biz_name", "Your Business")
    city  = city_only(data.get("service_area", "Your City"))
    phone = phone_clean(data.get("phone", "(555) 000-0000"))
    phone_d = phone_digits(data.get("phone", "5550000000"))

    svc_dir = output_dir / "services"
    svc_dir.mkdir(exist_ok=True)

    # Use repo template as base if exists, otherwise generate minimal
    repo_template = Path("/home/claude/LazyAI/website-template-v2/services/template.html")

    for slug, title in services:
        if repo_template.exists():
            content = repo_template.read_text()
            content = content.replace("Roof Repair in Austin | Lone Star Roofing", f"{title} in {city} | {biz}")
            content = content.replace("Expert roof repair in Austin", f"Expert {title.lower()} in {city}")
            content = content.replace("Roof Repair in Austin", f"{title} in {city}")
            content = content.replace("Lone Star Roofing", biz)
            content = content.replace("Austin", city)
            content = content.replace("(512) 555-1234", phone)
            content = content.replace("+15125551234", f"+1{phone_d}")
            content = content.replace("lonestarroofing.com", data.get("site_url", "example.com").replace("https://", "").replace("http://", ""))
        else:
            content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} in {city} | {biz}</title>
<meta name="description" content="Professional {title.lower()} in {city}. Fast response, quality work. Call {phone} today.">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<nav class="nav"><div class="container nav__inner">
  <a href="/" class="nav__logo">{biz}</a>
  <a href="tel:+1{phone_d}" class="nav__phone">📞 {phone}</a>
</div></nav>
<section class="hero" style="min-height:50vh">
  <div class="container hero__content">
    <h1>{title} in {city}</h1>
    <p>Professional {title.lower()} services — fast response, quality work, honest pricing.</p>
    <a href="tel:+1{phone_d}" class="btn btn--accent">📞 Call {phone}</a>
  </div>
</section>
<section class="lead-capture" id="estimate">
  <div class="container">
    <h2>Get a Free Estimate</h2>
    <form class="lead-capture__form" id="leadForm">
      <input type="text" name="name" placeholder="Your Name" required>
      <input type="tel" name="phone" placeholder="Phone Number" required>
      <input type="hidden" name="service" value="{title}">
      <button type="submit" class="btn">Get My Free Estimate</button>
    </form>
  </div>
</section>
<script src="../js/main.js" defer></script>
</body></html>"""

        (svc_dir / f"{slug}.html").write_text(content)

# ── Main homepage template injection ─────────────────────────────────────────
def build_homepage(data: dict, output_dir: Path, preset: dict):
    src = TEMPLATE_DIR / "index.html"
    if not src.exists():
        raise FileNotFoundError(f"Template not found: {src}")

    content = src.read_text()

    biz    = data.get("biz_name", "Your Business")
    city   = city_only(data.get("service_area", "Your City"))
    phone  = phone_clean(data.get("phone", "(555) 000-0000"))
    phone_d = phone_digits(data.get("phone", "5550000000"))
    tagline = data.get("tagline", f"Trusted {data.get('industry','').lower()} services in {city}.")
    plan   = data.get("plan", "growth")
    years  = data.get("years_in_business", "")
    rating_v = data.get("rating_value", "")
    rating_c = data.get("review_count", "")

    # --- HEAD replacement ---
    seo = generate_seo_meta(data, preset)
    ld  = generate_json_ld(data, preset)
    font_url = preset.get("fonts", "Inter:wght@400;600")

    # Remove the original template <title> and old <meta name="description"> to avoid duplicates
    content = re.sub(r'<title>[^<]*</title>\s*', '', content, count=1)
    content = re.sub(r'<meta\s+name="description"[^>]*/>\s*', '', content, count=1)
    content = re.sub(r'<meta\s+property="og:title"[^>]*/>\s*', '', content, count=1)
    content = re.sub(r'<meta\s+property="og:description"[^>]*/>\s*', '', content, count=1)
    content = re.sub(r'<meta\s+property="og:type"[^>]*/>\s*', '', content, count=1)
    content = re.sub(r'<meta\s+property="og:url"[^>]*/>\s*', '', content, count=1)
    # Remove original JSON-LD block (we'll inject a clean one)
    content = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', content, count=1, flags=re.DOTALL)

    if "<head>" in content:
        content = content.replace(
            "<head>",
            f"<head>\n{seo}\n{ld}\n"
            f'<link href="https://fonts.googleapis.com/css2?family={font_url}&display=swap" rel="stylesheet">\n'
            f"<style>:root{{--color-primary:{preset['primary']};--color-accent:{preset['accent']};}}</style>"
        )

    # --- Business name (all occurrences) ---
    content = content.replace("Lone Star Roofing", biz)
    content = content.replace("Lone Star", biz)
    content = content.replace("lonestarroofing.com", data.get("site_url", "").replace("https://","").replace("http://","") or "example.com")
    content = content.replace("info@lonestarroofing.com", data.get("email", f"info@example.com"))
    content = content.replace("Jake Henderson, Owner &amp; Founder", f"{data.get('contact_name', 'The Owner')}, Owner &amp; Founder")

    # --- City ---
    content = content.replace("Austin, TX", data.get("service_area", city))
    content = content.replace("Austin&amp;s", f"{city}&amp;s")
    # Replace plain "Austin" ONLY in text contexts (avoid URLs)
    content = re.sub(r'\bAustin\b(?![,.]?\s*TX)', city, content)

    # --- Phone ---
    content = content.replace("(512) 555-1234", phone)
    content = content.replace("+15125551234", f"+1{phone_d}")
    content = content.replace("tel:+15125551234", f"tel:+1{phone_d}")

    # --- Hero headline ---
    industry = data.get("industry", "Service")
    hero_hl = data.get("tagline") or f"{city}'s Trusted {industry} Contractor"
    content = content.replace(
        "Austin's <span class=\"hero__title-highlight\">Premium Roofing</span> &amp; Exterior Contractor",
        f"{city}'s <span class=\"hero__title-highlight\">{industry}</span> Experts"
    )
    content = content.replace(
        "Family-owned since 2010. We handle everything from emergency roof repairs to full replacements — with honest pricing, quality materials, and a 10-year workmanship guarantee.",
        tagline
    )

    # --- Rating badge ---
    if rating_v and rating_c:
        content = content.replace("4.9 Stars &middot; 287 Reviews", f"{rating_v} Stars &middot; {rating_c} Reviews")
        content = content.replace('"4.9"', f'"{rating_v}"')
        content = content.replace('"287"', f'"{rating_c}"')
    else:
        # Remove badge entirely if no real data
        content = re.sub(r'<div class="hero__badge"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # --- Trust bar ---
    since = f"Since {2025 - int(years)}" if years and str(years).isdigit() else "Locally Owned"
    content = content.replace("Since 2010", since)
    content = content.replace("Serving Austin", f"Serving {city}")

    # --- Service cards ---
    service_cards = generate_service_cards(data)
    service_cards = service_cards.replace("{{{{CITY}}}}", city)  # resolve deferred city token
    # Replace the services grid content
    services_grid_pattern = r'(<div class="services__grid">)(.*?)(</div>\s*</div>\s*</section>)'
    new_grid = rf'\g<1>\n{service_cards}\n      </div>\g<3>'
    content = re.sub(services_grid_pattern, new_grid, content, flags=re.DOTALL, count=1)

    # --- Service options in lead form ---
    service_options = generate_service_options(data)
    content = re.sub(
        r'(<select[^>]*name="service"[^>]*>).*?(</select>)',
        rf'\1\n          <option value="">What do you need help with?</option>\n{service_options}\n          <option value="other">Something Else</option>\n        \2',
        content, flags=re.DOTALL
    )

    # --- Workforce panel (WebStaff differentiator, inject before footer) ---
    workforce_html = generate_workforce_panel(plan)
    workforce_section = f"""
  <!-- ================================================================
       WEBSTAFF AI WORKFORCE (powered by WebStaff.com)
       ================================================================ -->
  <section class="section section--alt workforce-section" id="ai-office">
    <div class="container">
      <div class="text-center">
        <span class="section-label">Powered by WebStaff</span>
        <h2 class="section-title">Your AI Office Staff — Always On</h2>
        <p class="section-subtitle">
          Never miss a call, a lead, or a review again.
          Your AI team works 24/7 so you can stay on the tools.
        </p>
      </div>
      {workforce_html}
    </div>
  </section>"""
    content = content.replace("<!-- ================================================================\n       STICKY MOBILE BAR", workforce_section + "\n\n  <!-- ================================================================\n       STICKY MOBILE BAR")

    # --- Story section ---
    content = content.replace("Lone Star Roofing started in 2010", f"{biz} was founded with a simple idea")

    # --- Footer year ---
    content = content.replace("© 2026 Lone Star Roofing", f"© {datetime.now().year} {biz}")
    content = content.replace("Licenses: TECL #34567", data.get("certs", "Licensed & Insured"))

    # --- Add workforce CSS inline ---
    workforce_css = """
<style>
.workforce-section { padding: 80px 0; }
.workforce-panel { max-width: 900px; margin: 40px auto 0; }
.workforce-panel__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.workforce-panel__label { font-size: 18px; font-weight: 700; color: var(--color-text-primary, #111); }
.workforce-panel__plan { font-size: 13px; font-weight: 600; background: var(--color-accent, #3b82f6); color: white; padding: 4px 12px; border-radius: 999px; text-transform: uppercase; letter-spacing: .05em; }
.workforce-dept { margin-bottom: 24px; }
.workforce-dept__name { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #888; margin-bottom: 12px; }
.workforce-dept__staff { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }
.workforce-member { border-radius: 10px; padding: 14px 16px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; gap: 4px; transition: transform .15s; }
.workforce-member--active { background: #f0fdf4; border-color: #16a34a; }
.workforce-member--inactive { background: #f9fafb; opacity: .55; }
.workforce-member__name { font-size: 14px; font-weight: 700; color: #111; }
.workforce-member__desc { font-size: 12px; color: #555; }
.workforce-member__badge { font-size: 11px; font-weight: 600; margin-top: 6px; }
.workforce-member--active .workforce-member__badge { color: #16a34a; }
.workforce-member--inactive .workforce-member__badge { color: #999; }
@media (max-width: 600px) { .workforce-dept__staff { grid-template-columns: 1fr 1fr; } }
</style>"""
    content = content.replace("</head>", workforce_css + "\n</head>")

    (output_dir / "index.html").write_text(content)

# ── Validation ────────────────────────────────────────────────────────────────
REQUIRED_FIELDS = ["biz_name", "phone", "industry", "service_area", "plan"]

def validate(data: dict) -> list[str]:
    errors = []
    for f in REQUIRED_FIELDS:
        if not data.get(f):
            errors.append(f"Missing required field: {f}")
    valid_plans = ["essentials", "growth", "pro"]
    if data.get("plan") and data["plan"].lower() not in valid_plans:
        errors.append(f"plan must be one of: {', '.join(valid_plans)}")
    if data.get("rating_value") and not data.get("review_count"):
        errors.append("rating_value provided without review_count — omit both or provide both")
    return errors

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="WebStaff Site Generator")
    p.add_argument("--intake",    required=True, help="Path to intake JSON")
    p.add_argument("--validate",  action="store_true", help="Validate intake and exit")
    p.add_argument("--deploy",    action="store_true", help="Print deploy commands after build")
    p.add_argument("--platform",  default="netlify", choices=["netlify","vercel"])
    args = p.parse_args()

    with open(args.intake, "r") as f:
        data = json.load(f)

    data["plan"] = data.get("plan", "growth").lower()

    errors = validate(data)
    if errors:
        for e in errors: print(f"❌ {e}")
        if args.validate:
            raise SystemExit(1)
        print("⚠️  Continuing with warnings…")
    elif args.validate:
        print("✅ Intake is valid.")
        return

    preset = INDUSTRY_PRESETS.get(data["industry"], INDUSTRY_PRESETS["Other"])
    biz_slug = slugify(data["biz_name"]) + "_" + datetime.now().strftime("%Y%m%d")
    output_dir = OUTPUT_BASE / biz_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy static assets
    for subdir in ["css", "js", "images"]:
        src = TEMPLATE_DIR / subdir
        dst = output_dir / subdir
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    build_homepage(data, output_dir, preset)
    generate_service_pages(data, output_dir)

    # Netlify config
    netlify_src = Path(__file__).parent.parent / "netlify.toml"
    if netlify_src.exists():
        shutil.copy(netlify_src, output_dir / "netlify.toml")

    # Build manifest
    manifest = {
        "built_at": datetime.now().isoformat(),
        "biz_name": data["biz_name"],
        "plan": data["plan"],
        "active_staff": WORKFORCE_BY_PLAN.get(data["plan"], []),
        "industry": data["industry"],
        "city": city_only(data.get("service_area", "")),
    }
    (output_dir / "webstaff-manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"✅ Built: {data['biz_name']}")
    print(f"   Output: {output_dir}")
    print(f"   Plan:   {data['plan'].title()}  |  Staff: {len(WORKFORCE_BY_PLAN.get(data['plan'],[])):,} active")

    if args.deploy:
        print(f"\n🚀 Deploy commands ({args.platform}):")
        if args.platform == "netlify":
            print(f"   cd {output_dir} && netlify deploy --prod --dir .")
        else:
            print(f"   cd {output_dir} && vercel --prod")

if __name__ == "__main__":
    main()
