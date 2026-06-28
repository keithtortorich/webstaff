#!/usr/bin/env python3
"""
WebStaff Build API
Receives intake JSON → runs site_generator → returns manifest + download link.

Run locally:
  python3 api/build.py
  # API at http://localhost:5050

POST /api/build  — body: intake JSON (see tests/fixtures/example_intake.json)
GET  /api/health — health check
"""

import json, subprocess, sys, os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Resolve paths relative to project root (one level up from api/)
ROOT = Path(__file__).parent.parent
GENERATOR = ROOT / "builder" / "site_generator.py"
CLIENTS_DIR = ROOT / "clients"
FIXTURES_DIR = ROOT / "tests" / "fixtures"

app = Flask(__name__)
CORS(app, origins=["http://localhost:*", "https://*.netlify.app", "https://webstaff.com"])

# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "generator": str(GENERATOR.exists())})

# ── Build ─────────────────────────────────────────────────────────────────────
@app.route("/api/build", methods=["POST"])
def build():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Write temp intake file
    intake_path = FIXTURES_DIR / "temp_intake.json"
    intake_path.parent.mkdir(parents=True, exist_ok=True)
    intake_path.write_text(json.dumps(data))

    # Run generator
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--intake", str(intake_path)],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0:
        return jsonify({
            "error": "Build failed",
            "detail": result.stderr or result.stdout,
        }), 500

    # Find generated output dir (newest under clients/)
    dirs = sorted(
        [d for d in CLIENTS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        return jsonify({"error": "No output directory found"}), 500

    out_dir = dirs[0]
    manifest_path = out_dir / "webstaff-manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    return jsonify({
        "status":    "built",
        "site_slug": out_dir.name,
        "preview":   f"/clients/{out_dir.name}/index.html",
        "manifest":  manifest,
        "stdout":    result.stdout,
    })

# ── Serve generated client sites for local preview ───────────────────────────
@app.route("/clients/<path:filename>")
def serve_client(filename):
    return send_from_directory(str(CLIENTS_DIR), filename)

# ── Serve intake form ─────────────────────────────────────────────────────────
@app.route("/", defaults={"filename": "index.html"})
@app.route("/<path:filename>")
def serve_intake(filename):
    intake_dir = ROOT / "intake"
    if (intake_dir / filename).exists():
        return send_from_directory(str(intake_dir), filename)
    return "Not found", 404

# ── Lead capture (from generated client sites) ───────────────────────────────
@app.route("/api/leads", methods=["POST"])
def capture_lead():
    """
    Receives leads from generated client site forms.
    In production: forward to WebStaff CRM / SMS workflow.
    """
    data = request.get_json(force=True) or {}
    # Log to file for MVP / investor demo
    log_path = ROOT / "clients" / "leads.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps({"lead": data, "ts": __import__("datetime").datetime.now().isoformat()}) + "\n")
    return jsonify({"status": "received", "message": "We'll be in touch within 1 hour."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"WebStaff Build API — http://localhost:{port}")
    print(f"  POST /api/build  — trigger site build")
    print(f"  GET  /api/health — health check")
    print(f"  GET  /           — intake form")
    app.run(debug=True, port=port)
