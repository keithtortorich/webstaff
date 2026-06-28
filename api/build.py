#!/usr/bin/env python3
"""
WebStaff Build API
------------------
Receives intake JSON from intake.html, writes a temp file,
calls site_generator.py, and returns build results.

Run locally:  python3 api/build.py
Production:   gunicorn api.build:app
"""

import sys
import os
import json
import tempfile
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure builder module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)  # Allow intake.html on any origin during dev

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("WebStaff.API")

BUILDER_SCRIPT = Path(__file__).parent.parent / "builder" / "site_generator.py"
CLIENTS_DIR    = Path(__file__).parent.parent / "clients"
VALID_PLANS    = {"essentials", "growth", "pro"}
VALID_INDUSTRIES = {
    "Contractor", "Restaurant", "Med Spa", "Dentist", "Plumber", "Other"
}


# ── Validation ────────────────────────────────────────────────────────────────

def validate_intake(data: dict) -> list[str]:
    errors = []
    for field in ["biz_name", "phone", "industry", "service_area", "plan"]:
        if not data.get(field):
            errors.append(f"Missing required field: '{field}'")
    if data.get("plan") and data["plan"].lower() not in VALID_PLANS:
        errors.append(f"Invalid plan '{data['plan']}'. Must be: {', '.join(VALID_PLANS)}")
    if data.get("industry") and data["industry"] not in VALID_INDUSTRIES:
        errors.append(f"Unknown industry '{data['industry']}'")
    return errors


# ── Build trigger ─────────────────────────────────────────────────────────────

def run_build(intake_data: dict) -> dict:
    """Write intake to temp file, call site_generator.py, return result."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(intake_data, tmp, indent=2)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, str(BUILDER_SCRIPT), "--intake", tmp_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        log.info(f"Builder stdout: {result.stdout.strip()}")
        if result.returncode != 0:
            log.error(f"Builder stderr: {result.stderr.strip()}")
            raise RuntimeError(result.stderr.strip() or "Builder exited with error.")

        # Find the output directory from manifest
        slug = "".join(
            c if c.isalnum() else "_"
            for c in intake_data.get("biz_name", "client").lower()
        ).strip("_")
        date_stamp = datetime.now().strftime("%Y%m%d")
        output_dir = CLIENTS_DIR / f"{slug}_{date_stamp}"

        manifest_path = output_dir / "webstaff-manifest.json"
        manifest = {}
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

        return {
            "success": True,
            "output_dir": str(output_dir),
            "stdout": result.stdout.strip(),
            "manifest": manifest,
            "preview_url": f"/clients/{slug}_{date_stamp}/index.html",
        }

    finally:
        os.unlink(tmp_path)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/build", methods=["POST"])
def build():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body."}), 400

    errors = validate_intake(data)
    if errors:
        return jsonify({"error": "; ".join(errors)}), 422

    log.info(f"Build request: {data.get('biz_name')} / {data.get('plan')}")

    try:
        result = run_build(data)
        return jsonify(result), 200
    except RuntimeError as e:
        log.error(str(e))
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        log.exception("Unexpected build error")
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "brand": "WebStaff",
        "builder": str(BUILDER_SCRIPT),
        "builder_exists": BUILDER_SCRIPT.exists(),
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/plans", methods=["GET"])
def plans():
    """Return plan/workforce data for the intake form to consume."""
    from builder.site_generator import WORKFORCE_BY_PLAN
    return jsonify(WORKFORCE_BY_PLAN)


# ── Dev server ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    log.info(f"WebStaff Build API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
