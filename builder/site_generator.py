#!/usr/bin/env python3
"""
WebStaffr Site Generator
Intake JSON → fully deployed static client site

Usage:
    python builder/site_generator.py --intake tests/fixtures/example_intake.json
    python builder/site_generator.py --intake client.json --validate
    python builder/site_generator.py --intake client.json --deploy
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent.parent / "website-template-v2"
OUTPUT_BASE  = Path(__file__).parent.parent / "clients"
API_BASE     = os.getenv("BASE_URL", "http://localhost:8000")

# ── Industry presets (from perfect_site spec) ────────────────────────────────

INDUSTRY_PRESETS = {
    "Contractor": {
        "slug": "contractor",
        "font_family": "Oswald:wght@700&family=Inter:wght@400;600",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#1a1a1a",
        "accent": "#d97706",
        "icon": "🔨",
        "default_tagline": "Quality construction and remodeling — done right the first time.",
        "default_services": ["General Contracting", "Home Remodeling", "New Construction", "Renovation"],
    },
    "HVAC": {
        "slug": "hvac",
        "font_family": "Oswald:wght@700&family=Inter:wght@400;600",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#1e3a5f",
        "accent": "#0ea5e9",
        "icon": "❄️",
        "default_tagline": "Same-day HVAC service — keep your home comfortable year-round.",
        "default_services": ["AC Repair", "AC Installation", "Furnace Repair", "Duct Cleaning", "Emergency HVAC"],
    },
    "Plumber": {
        "slug": "plumber",
        "font_family": "Archivo+Black:wght@400&family=Inter:wght@400;600",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#1e3a8a",
        "accent": "#ef4444",
        "icon": "🔧",
        "default_tagline": "Plumbing emergencies handled fast — licensed & insured.",
        "default_services": ["Emergency Plumbing", "Pipe Repair", "Water Heater", "Drain Cleaning", "Leak Detection"],
    },
    "Electrician": {
        "slug": "electrician",
        "font_family": "Sora:wght@700&family=Inter:wght@400;500",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#1c1c1c",
        "accent": "#f59e0b",
        "icon": "⚡",
        "default_tagline": "Licensed electrician — safe, code-compliant, same-day service.",
        "default_services": ["Panel Upgrades", "Wiring & Rewiring", "EV Charger Install", "Lighting", "Emergency Electrical"],
    },
    "Roofing": {
        "slug": "roofing",
        "font_family": "Oswald:wght@700&family=Inter:wght@400;600",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#292524",
        "accent": "#dc2626",
        "icon": "🏠",
        "default_tagline": "Protect your home — roof repair & replacement done right.",
        "default_services": ["Roof Repair", "Roof Replacement", "Storm Damage", "Gutters", "Free Inspection"],
    },
    "Restaurant": {
        "slug": "restaurant",
        "font_family": "Playfair+Display:wght@700&family=Inter:wght@400;500",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#78350f",
        "accent": "#b45309",
        "icon": "🍽️",
        "default_tagline": "Fresh ingredients, unforgettable flavors — come dine with us.",
        "default_services": ["Dine-In", "Takeout", "Catering", "Private Events", "Happy Hour"],
    },
    "Med Spa": {
        "slug": "medspa",
        "font_family": "Cormorant+Garamond:wght@700&family=Inter:wght@400;500",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#4c1d95",
        "accent": "#c026d3",
        "icon": "✨",
        "default_tagline": "Luxury treatments. Real results. You deserve to feel remarkable.",
        "default_services": ["Botox & Fillers", "Laser Treatments", "Hydrafacial", "Body Contouring", "Skin Rejuvenation"],
    },
    "Dentist": {
        "slug": "dentist",
        "font_family": "Outfit:wght@600&family=Inter:wght@400;500",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#0f766e",
        "accent": "#14b8a6",
        "icon": "🦷",
        "default_tagline": "Gentle, modern dentistry — smile with confidence.",
        "default_services": ["Teeth Whitening", "Invisalign", "Dental Implants", "Emergency Dentistry", "Cleanings & Exams"],
    },
    "Salon": {
        "slug": "salon",
        "font_family": "DM+Serif+Display:wght@400&family=Inter:wght@400;500",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#831843",
        "accent": "#ec4899",
        "icon": "💇",
        "default_tagline": "Expert cuts, color, and style — where you feel your best.",
        "default_services": ["Haircuts & Styling", "Color & Highlights", "Balayage", "Keratin Treatment", "Blowouts"],
    },
    "Other": {
        "slug": "other",
        "font_family": "Inter:wght@400;600;800",
        "font_css": "--font:'Inter',sans-serif;",
        "primary": "#1e40af",
        "accent": "#3b82f6",
        "icon": "🏢",
        "default_tagline": "Professional service you can count on.",
        "default_services": ["Service 1", "Service 2", "Service 3"],
    },
}

PLAN_STAFF = {
    "essentials": ["Office Manager"],
    "growth":     ["Receptionist", "Lead Coordinator", "Reputation Manager", "Sales Consultant", "Office Manager"],
    "pro":        ["Receptionist", "Lead Coordinator", "Reputation Manager", "Sales Consultant",
                   "Office Manager", "Marketing Coordinator", "Growth Manager"],
}


# ── Validation ────────────────────────────────────────────────────────────────

def validate_intake(data: dict) -> list[str]:
    errors = []
    for f in ["biz_name", "phone", "plan"]:
        if not data.get(f):
            errors.append(f"Missing required field: {f}")
    if data.get("plan") and data["plan"] not in ("essentials", "growth", "pro"):
        errors.append("plan must be: essentials | growth | pro")
    if data.get("rating_value") and not (1.0 <= float(data["rating_value"]) <= 5.0):
        errors.append("rating_value must be between 1.0 and 5.0")
    return errors


# ── HTML fragment builders ─────────────────────────────────────────────────────

SERVICE_ICONS = {
    "ac repair": "❄️", "ac install": "🔧", "furnace": "🔥", "duct": "💨",
    "emergency": "🚨", "plumb": "🔧", "pipe": "🔩", "water heater": "🌡️",
    "drain": "🌊", "electric": "⚡", "panel": "🔌", "wiring": "💡",
    "roof": "🏠", "gutter": "🌧️", "storm": "⛈️", "remodel": "🔨",
    "paint": "🎨", "floor": "🪵", "tile": "🔲", "kitchen": "🍳",
    "bath": "🛁", "hvac": "❄️", "dental": "🦷", "laser": "✨",
    "botox": "💉", "skin": "🌸", "massage": "💆", "hair": "💇",
    "color": "🎨", "catering": "🍽️", "booking": "📅",
}

def _service_icon(name: str) -> str:
    name_lower = name.lower()
    for k, v in SERVICE_ICONS.items():
        if k in name_lower:
            return v
    return "✅"


def build_services_html(services: list[str], industry: str) -> str:
    preset = INDUSTRY_PRESETS.get(industry, INDUSTRY_PRESETS["Other"])
    cards = []
    for svc in services[:6]:  # cap at 6 per perfect_site spec
        icon = _service_icon(svc)
        cards.append(f"""      <div class="service-card">
        <div class="service-card__icon">{icon}</div>
        <h3>{svc}</h3>
        <p>Professional {svc.lower()} service — licensed, insured, and backed by our guarantee.</p>
        <a href="#contact" class="service-card__link">Get free estimate →</a>
      </div>""")
    return "\n".join(cards)


def build_footer_services_html(services: list[str]) -> str:
    return "\n".join(f'        <li><a href="#services">{s}</a></li>' for s in services[:5])


def build_social_links_html(data: dict) -> str:
    links = []
    for platform, label in [("facebook_url","Facebook"),("instagram_url","Instagram"),("google_url","Google")]:
        url = data.get(platform)
        if url:
            links.append(f'<a href="{url}" target="_blank" rel="noopener">{label}</a>')
    return " · ".join(links) if links else ""


# ── SEO / Schema injection ────────────────────────────────────────────────────

def build_seo_block(data: dict, preset: dict) -> str:
    city = (data.get("service_area","") or "").split(",")[0].strip()
    biz  = data.get("biz_name","")
    ind  = data.get("industry","")
    phone= data.get("phone","")
    url  = data.get("site_url","")

    title = f"{ind} in {city} | {biz}" if city else f"{biz} | {ind}"
    desc  = (
        f"Professional {ind.lower()} in {city}. "
        f"Fast response, quality work, licensed & insured. "
        f"Call {phone} today."
    ).strip()

    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": biz,
        "telephone": phone,
        "url": url,
        "description": desc,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressCountry": "US",
        },
        "priceRange": "$$",
    }
    if data.get("rating_value") and data.get("review_count"):
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(data["rating_value"]),
            "reviewCount": str(data["review_count"]),
        }
    if url:
        schema["sameAs"] = [url]

    schema_str = json.dumps(schema, indent=2)

    return f"""  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <script type="application/ld+json">
{schema_str}
  </script>"""


# ── Core build ────────────────────────────────────────────────────────────────

def sanitize_slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_") or "client"


def build_site(data: dict, output_dir: Path, debug: bool = False) -> bool:
    industry = data.get("industry", "Other")
    preset   = INDUSTRY_PRESETS.get(industry, INDUSTRY_PRESETS["Other"])
    services = data.get("services") or preset["default_services"]
    plan     = data.get("plan", "growth")

    # Copy template
    if TEMPLATE_DIR.exists():
        shutil.copytree(str(TEMPLATE_DIR), str(output_dir), dirs_exist_ok=True)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / "index.html"
    if not index_path.exists():
        print(f"  ⚠️  Template index.html missing at {TEMPLATE_DIR}")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. SEO block → inject before </head>
    seo_block = build_seo_block(data, preset)
    html = html.replace("  <!-- SEO + Schema injected by builder -->", seo_block)

    # 2. Google Font URL
    html = html.replace("{{FONT_FAMILY}}", preset["font_family"])

    # 3. Industry slug for CSS class
    html = html.replace("{{INDUSTRY_SLUG}}", preset["slug"])

    # 4. Inject client_id + api_base onto <body> for JS lead capture
    client_id = data.get("id", "")
    html = html.replace(
        f'class="industry-{preset["slug"]}"',
        f'class="industry-{preset["slug"]}" data-client-id="{client_id}" data-api-base="{API_BASE}"'
    )

    # 5. Inject industry CSS vars into <head>
    css_vars = (
        f'<style>:root{{'
        f'--primary:{preset["primary"]};'
        f'--accent:{preset["accent"]};'
        f'{preset["font_css"]}'
        f'}}</style>'
    )
    html = html.replace("</head>", f"  {css_vars}\n</head>")

    # 6. Services HTML
    services_html    = build_services_html(services, industry)
    footer_svc_html  = build_footer_services_html(services)
    social_html      = build_social_links_html(data)

    # 7. All placeholder replacements
    replacements = {
        "{{BIZ_NAME}}":           data.get("biz_name", ""),
        "{{PHONE}}":              data.get("phone", ""),
        "{{EMAIL}}":              data.get("email", ""),
        "{{SERVICE_AREA}}":       data.get("service_area", ""),
        "{{INDUSTRY}}":           industry,
        "{{TAGLINE}}":            data.get("tagline") or preset["default_tagline"],
        "{{RATING_VALUE}}":       str(data.get("rating_value", "5.0")),
        "{{REVIEW_COUNT}}":       str(data.get("review_count", "100+")),
        "{{YEARS_IN_BIZ}}":       str(data.get("years_in_biz", "10")),
        "{{LICENSE_NUMBER}}":     data.get("license_number", ""),
        "{{GOOGLE_REVIEW_LINK}}": data.get("google_review_link", "#"),
        "{{SERVICES_HTML}}":      services_html,
        "{{FOOTER_SERVICES_HTML}}": footer_svc_html,
        "{{SOCIAL_LINKS_HTML}}":  social_html,
        "{{YEAR}}":               str(datetime.now().year),
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Write netlify.toml for this site
    (output_dir / "netlify.toml").write_text(
        '[build]\n  publish = "."\n\n'
        '[[headers]]\n  for = "/*"\n'
        '  [headers.values]\n'
        '    X-Frame-Options = "SAMEORIGIN"\n'
        '    X-Content-Type-Options = "nosniff"\n'
    )

    # Write manifest
    manifest = {
        "generated_at":      datetime.utcnow().isoformat() + "Z",
        "webstaffr_version": "1.0.0",
        "biz_name":          data.get("biz_name"),
        "client_id":         client_id or "not-yet-registered",
        "plan":              plan,
        "industry":          industry,
        "service_area":      data.get("service_area"),
        "active_staff":      PLAN_STAFF.get(plan, PLAN_STAFF["growth"]),
        "api_base":          API_BASE,
    }
    with open(output_dir / "webstaffr-manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    if debug:
        print(f"  Preset used: {industry}")
        print(f"  Services: {services}")
        print(f"  Active staff: {PLAN_STAFF.get(plan)}")
        print(f"  Output files: {sorted(p.name for p in output_dir.iterdir())}")

    return True


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="WebStaffr Site Builder")
    parser.add_argument("--intake",   required=True, help="Path to intake JSON")
    parser.add_argument("--validate", action="store_true", help="Validate only — no build")
    parser.add_argument("--deploy",   action="store_true", help="Print deploy commands after build")
    parser.add_argument("--platform", default="netlify", choices=["netlify", "vercel"])
    parser.add_argument("--debug",    action="store_true")
    args = parser.parse_args()

    with open(args.intake, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = validate_intake(data)
    if errors:
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)

    if args.validate:
        print(f"✅ Intake valid: {data['biz_name']} [{data['plan']}]")
        return

    slug      = sanitize_slug(data["biz_name"])
    ts        = datetime.now().strftime("%Y%m%d_%H%M")
    out_dir   = OUTPUT_BASE / f"{slug}_{ts}"

    print(f"🏗  Building: {data['biz_name']} ({data.get('industry','?')} · {data['plan']})")
    ok = build_site(data, out_dir, debug=args.debug)

    if ok:
        print(f"✅ Site built → {out_dir}")
        if args.deploy:
            if args.platform == "netlify":
                print(f"\n🚀 Deploy:\n  cd {out_dir}\n  npx netlify deploy --prod --dir .")
            else:
                print(f"\n🚀 Deploy:\n  cd {out_dir}\n  npx vercel --prod")
    else:
        print("❌ Build failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
