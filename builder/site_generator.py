#!/usr/bin/env python3
"""
WebStaff Client Site Generator
--------------------------------
Builds client websites and injects AI workforce configuration
based on the WebStaff positioning: "We run the office while
contractors run the business."

Plans:
  essentials  - $197/mo  - Website Operations Manager only
  growth      - $497/mo  - Full front office AI staff (recommended)
  pro         - $997/mo  - Growth + Marketing, SEO, CRM, Strategy
"""

import os
import sys
import shutil
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# ── Constants ────────────────────────────────────────────────────────────────

TEMPLATE_DIR = "website-template-v2"
OUTPUT_BASE = "clients"
BRAND = "WebStaff"

# ── Industry Presets ─────────────────────────────────────────────────────────
# FIX: presets are now actually applied during site generation

INDUSTRY_PRESETS = {
    "Contractor": {
        "fonts": "Oswald:wght@700&family=Inter:wght@400;600",
        "primary": "#1a1a1a",
        "accent": "#d97706",
        "schema_type": "HomeAndConstructionBusiness",
    },
    "Restaurant": {
        "fonts": "Playfair+Display:wght@700&family=Inter:wght@400;500",
        "primary": "#78350f",
        "accent": "#b45309",
        "schema_type": "Restaurant",
    },
    "Med Spa": {
        "fonts": "Cormorant+Garamond:wght@700&family=Inter:wght@400;500",
        "primary": "#4c1d95",
        "accent": "#c026d3",
        "schema_type": "HealthAndBeautyBusiness",
    },
    "Dentist": {
        "fonts": "Outfit:wght@600&family=Inter:wght@400;500",
        "primary": "#0f766e",
        "accent": "#14b8a6",
        "schema_type": "Dentist",
    },
    "Plumber": {
        "fonts": "Archivo+Black:wght@400&family=Inter:wght@400;600",
        "primary": "#1e3a8a",
        "accent": "#ef4444",
        "schema_type": "Plumber",
    },
    "Other": {
        "fonts": "Inter:wght@400;600",
        "primary": "#1e40af",
        "accent": "#3b82f6",
        "schema_type": "LocalBusiness",
    },
}

# ── WebStaff AI Workforce Definitions ────────────────────────────────────────
# Each entry maps to a staff role per the WebStaff positioning strategy.
# Keys align with plan tiers: essentials / growth / pro

WORKFORCE_BY_PLAN = {
    "essentials": [
        {"role": "Website Operations Manager", "feature": "hosting", "tagline": "Keeps your business online."},
    ],
    "growth": [
        {"role": "Website Operations Manager", "feature": "hosting",         "tagline": "Keeps your business online."},
        {"role": "Receptionist",               "feature": "voice_agent",     "tagline": "Answers every call. Books every lead."},
        {"role": "Lead Coordinator",           "feature": "speed_to_lead",   "tagline": "Replies instantly and keeps leads warm."},
        {"role": "Reputation Manager",         "feature": "review_chaser",   "tagline": "Gets more 5-star reviews automatically."},
        {"role": "Sales Consultant",           "feature": "sales_consultant","tagline": "Helps customers say yes to bigger jobs."},
    ],
    "pro": [
        {"role": "Website Operations Manager", "feature": "hosting",         "tagline": "Keeps your business online."},
        {"role": "Receptionist",               "feature": "voice_agent",     "tagline": "Answers every call. Books every lead."},
        {"role": "Lead Coordinator",           "feature": "speed_to_lead",   "tagline": "Replies instantly and keeps leads warm."},
        {"role": "Reputation Manager",         "feature": "review_chaser",   "tagline": "Gets more 5-star reviews automatically."},
        {"role": "Sales Consultant",           "feature": "sales_consultant","tagline": "Helps customers say yes to bigger jobs."},
        {"role": "Marketing Coordinator",      "feature": "social_posting",  "tagline": "Keeps your business visible every day."},
        {"role": "Growth Manager",             "feature": "seo_geo",         "tagline": "Brings in customers from Google and AI search."},
        {"role": "Service Advisor",            "feature": "repair_diagnosis","tagline": "Pre-qualifies customers before you arrive."},
    ],
}

VALID_PLANS = list(WORKFORCE_BY_PLAN.keys())

# ── Logging Setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(BRAND)

# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_name(name: str) -> str:
    """Convert business name to a safe directory slug."""
    cleaned = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")
    return cleaned or "client"


def parse_city(service_area: str) -> str:
    """Safely extract primary city from a service area string."""
    if not service_area:
        return "Your City"
    return service_area.split(",")[0].strip() or "Your City"


def validate_intake(data: dict) -> list[str]:
    """
    FIX: --validate flag is now functional.
    Returns a list of error strings; empty list means valid.
    """
    errors = []
    required = ["biz_name", "phone", "industry", "service_area", "plan"]
    for field in required:
        if not data.get(field):
            errors.append(f"Missing required field: '{field}'")

    plan = data.get("plan", "").lower()
    if plan and plan not in VALID_PLANS:
        errors.append(f"Invalid plan '{plan}'. Must be one of: {', '.join(VALID_PLANS)}")

    industry = data.get("industry", "")
    if industry and industry not in INDUSTRY_PRESETS:
        log.warning(f"Unknown industry '{industry}' — falling back to 'Other'.")

    return errors


def get_preset(industry: str) -> dict:
    return INDUSTRY_PRESETS.get(industry, INDUSTRY_PRESETS["Other"])


def get_workforce(plan: str) -> list[dict]:
    return WORKFORCE_BY_PLAN.get(plan.lower(), WORKFORCE_BY_PLAN["essentials"])

# ── HTML Generation ───────────────────────────────────────────────────────────

def generate_seo_meta(data: dict) -> str:
    """
    FIX: Description now reflects WebStaff positioning.
    """
    city = parse_city(data.get("service_area", ""))
    biz = data.get("biz_name", "Your Business")
    industry = data.get("industry", "Service")

    title = f"{industry} in {city} | {biz}"
    description = (
        f"{biz} serves {city} with professional {industry.lower()} services — "
        f"backed by a full AI office that answers every call, books every job, "
        f"and follows up every lead. Powered by {BRAND}."
    )
    return f"""
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="website">
    """.strip()


def generate_json_ld(data: dict) -> str:
    """
    FIX: schema_type is now industry-specific, not always LocalBusiness.
    FIX: Hardcoded fake ratings removed; only included when real data exists.
    FIX: URL pulled from intake data.
    """
    preset = get_preset(data.get("industry", "Other"))
    schema: dict = {
        "@context": "https://schema.org",
        "@type": preset["schema_type"],
        "name": data.get("biz_name"),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": parse_city(data.get("service_area", "")),
        },
        "telephone": data.get("phone"),
    }
    if data.get("site_url"):
        schema["url"] = data["site_url"]

    # Only include rating if real values are provided in intake
    rating_value = data.get("rating_value")
    review_count = data.get("review_count")
    if rating_value and review_count:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(rating_value),
            "reviewCount": str(review_count),
        }

    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def generate_css_variables(data: dict) -> str:
    """
    FIX: Industry fonts and colors are now actually injected into the page.
    """
    preset = get_preset(data.get("industry", "Other"))
    return f"""
    <style>
      :root {{
        --color-primary: {preset['primary']};
        --color-accent:  {preset['accent']};
      }}
    </style>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family={preset['fonts']}&display=swap" rel="stylesheet">
    """.strip()


def generate_workforce_block(data: dict) -> str:
    """
    NEW: Renders an HTML comment block listing the active AI staff for this
    client, aligned with WebStaff's 'hire your AI office' positioning.
    Also embeds a data attribute used by WebStaff JS modules to activate features.
    """
    plan = data.get("plan", "essentials").lower()
    workforce = get_workforce(plan)
    staff_list = "\n".join(
        f"  <!-- [{w['role']}] {w['tagline']} -->" for w in workforce
    )
    features_json = json.dumps([w["feature"] for w in workforce])
    return f"""
<!-- ╔══════════════════════════════════════════════╗
     ║  WebStaff AI Office — Active Staff Roster  ║
     ║  Plan: {plan.upper():<38}║
     ╚══════════════════════════════════════════════╝
{staff_list}
-->
<div id="webstaff-config"
     data-plan="{plan}"
     data-features='{features_json}'
     style="display:none;"
     aria-hidden="true">
</div>
    """.strip()


def replace_template_variables(content: str, data: dict) -> str:
    """
    FIX: Template placeholders are now actually replaced with client data.
    Supports {{variable_name}} syntax in HTML templates.
    """
    city = parse_city(data.get("service_area", ""))
    plan = data.get("plan", "essentials").lower()
    workforce = get_workforce(plan)
    staff_names = ", ".join(w["role"] for w in workforce)

    replacements = {
        "{{biz_name}}":     data.get("biz_name", "Your Business"),
        "{{phone}}":        data.get("phone", ""),
        "{{email}}":        data.get("email", ""),
        "{{industry}}":     data.get("industry", "Service"),
        "{{service_area}}": data.get("service_area", ""),
        "{{city}}":         city,
        "{{plan}}":         plan.title(),
        "{{tagline}}":      data.get("tagline", f"Serving {city} and surrounding areas."),
        "{{staff_roster}}": staff_names,
        "{{year}}":         str(datetime.now().year),
        "{{brand}}":        BRAND,
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content

# ── Build Manifest ────────────────────────────────────────────────────────────

def write_manifest(output_dir: Path, data: dict) -> None:
    """
    NEW: Writes a JSON manifest so builds are auditable.
    Tracks client, plan, workforce, and build timestamp.
    """
    plan = data.get("plan", "essentials").lower()
    manifest = {
        "brand": BRAND,
        "built_at": datetime.now().isoformat(),
        "client": {
            "biz_name": data.get("biz_name"),
            "industry": data.get("industry"),
            "service_area": data.get("service_area"),
            "phone": data.get("phone"),
            "plan": plan,
        },
        "ai_workforce": get_workforce(plan),
        "output_dir": str(output_dir),
    }
    manifest_path = output_dir / "webstaff-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log.info(f"Manifest written → {manifest_path}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=f"{BRAND} Site Builder — AI Workforce for Home Service Businesses"
    )
    parser.add_argument("--intake",   required=True, help="Path to client intake JSON")
    parser.add_argument("--deploy",   action="store_true", help="Trigger deploy after build")
    parser.add_argument("--platform", default="netlify", choices=["netlify", "vercel"])
    parser.add_argument("--validate", action="store_true", help="Validate intake JSON and exit")
    args = parser.parse_args()

    # Load intake
    intake_path = Path(args.intake)
    if not intake_path.exists():
        log.error(f"Intake file not found: {intake_path}")
        sys.exit(1)

    with open(intake_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # FIX: --validate is now functional
    errors = validate_intake(data)
    if errors:
        for e in errors:
            log.error(f"Validation error: {e}")
        if args.validate or True:  # always block on hard errors
            sys.exit(1)

    if args.validate:
        log.info("✅ Intake is valid.")
        sys.exit(0)

    # Output directory — includes date stamp to track rebuilds
    client_slug = sanitize_name(data.get("biz_name", "client"))
    date_stamp = datetime.now().strftime("%Y%m%d")
    output_dir = Path(OUTPUT_BASE) / f"{client_slug}_{date_stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Building site for '{data.get('biz_name')}' → {output_dir}")

    # Copy template
    template_path = Path(TEMPLATE_DIR)
    if template_path.exists():
        shutil.copytree(template_path, output_dir, dirs_exist_ok=True)
        log.info(f"Template copied from {TEMPLATE_DIR}")
    else:
        log.warning(f"Template directory '{TEMPLATE_DIR}' not found — building with injected content only.")

    # Process index.html
    # FIX: index.html processing is now guarded properly
    index_path = output_dir / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace {{placeholders}} first
        content = replace_template_variables(content, data)

        # Inject into <head>
        head_injections = "\n".join([
            generate_seo_meta(data),
            generate_json_ld(data),
            generate_css_variables(data),   # FIX: now actually applied
        ])
        content = content.replace("<head>", f"<head>\n{head_injections}\n", 1)

        # Inject workforce config before </body>
        workforce_block = generate_workforce_block(data)
        content = content.replace("</body>", f"\n{workforce_block}\n</body>", 1)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        log.info("index.html updated with client data and AI workforce config.")
    else:
        log.warning("No index.html found in output directory — skipping HTML processing.")

    # Write build manifest
    write_manifest(output_dir, data)

    # Summary
    plan = data.get("plan", "essentials").title()
    workforce = get_workforce(data.get("plan", "essentials"))
    staff_summary = ", ".join(w["role"] for w in workforce)

    print(f"\n✅  {BRAND} site built for {data.get('biz_name')}")
    print(f"    Plan:      {plan}")
    print(f"    Directory: {output_dir}")
    print(f"    AI Staff:  {staff_summary}")

    if args.deploy:
        print(f"\n🚀  Deploy target: {args.platform.upper()} — ready for production.")


if __name__ == "__main__":
    main()
