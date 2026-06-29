"""
WebStaff Webhook Router
Receives all inbound events and dispatches to the correct agent handler.

Routes:
  POST /webhooks/call          → Receptionist (Twilio call webhook)
  POST /webhooks/lead          → Lead Coordinator (form submission)
  POST /webhooks/job-complete  → Reputation Manager (job close)
  POST /webhooks/lead-aged     → Sales Consultant (48h no-book)
  POST /webhooks/uptime        → Website Ops (UptimeRobot alert)
"""

from flask import Flask, request, jsonify
import logging
import hmac
import hashlib
import os

logger = logging.getLogger(__name__)
app = Flask(__name__)

TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
WEBSTAFF_WEBHOOK_SECRET = os.environ.get("WEBSTAFF_WEBHOOK_SECRET", "")


def verify_twilio(request) -> bool:
    """Verify Twilio webhook signature."""
    if not TWILIO_AUTH_TOKEN:
        return True  # Dev mode — skip verification
    # TODO: implement full Twilio signature validation
    return True


def dispatch(agent_slug: str, event: dict) -> dict:
    """Import and call the correct agent handler."""
    try:
        import importlib
        module = importlib.import_module(f"agents.{agent_slug}.handler")
        return module.handle(event)
    except NotImplementedError:
        return {"status": "pending", "message": f"{agent_slug} not yet implemented"}
    except Exception as e:
        logger.error(f"Agent {agent_slug} error: {e}")
        return {"status": "error", "message": str(e)}


@app.route("/webhooks/call", methods=["POST"])
def webhook_call():
    """Twilio inbound call → Receptionist"""
    if not verify_twilio(request):
        return jsonify({"error": "unauthorized"}), 401
    event = {
        "type": "inbound_call",
        "caller": request.form.get("From", ""),
        "called": request.form.get("To", ""),
        "call_sid": request.form.get("CallSid", ""),
        "client_id": request.args.get("client_id", ""),
    }
    result = dispatch("receptionist", event)
    return jsonify(result)


@app.route("/webhooks/lead", methods=["POST"])
def webhook_lead():
    """Form submission → Lead Coordinator"""
    data = request.get_json(force=True) or {}
    event = {
        "type": "new_lead",
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "service": data.get("service", ""),
        "message": data.get("message", ""),
        "source": data.get("source_site", ""),
        "client_id": data.get("webstaff_client", ""),
    }
    result = dispatch("lead_coordinator", event)
    return jsonify(result)


@app.route("/webhooks/job-complete", methods=["POST"])
def webhook_job_complete():
    """Job closed → Reputation Manager"""
    data = request.get_json(force=True) or {}
    event = {
        "type": "job_complete",
        "customer_name": data.get("customer_name", ""),
        "customer_phone": data.get("customer_phone", ""),
        "service": data.get("service", ""),
        "contractor_name": data.get("contractor_name", ""),
        "gbp_review_link": data.get("gbp_review_link", ""),
        "client_id": data.get("client_id", ""),
    }
    result = dispatch("reputation_manager", event)
    return jsonify(result)


@app.route("/webhooks/lead-aged", methods=["POST"])
def webhook_lead_aged():
    """48h no-booking → Sales Consultant"""
    data = request.get_json(force=True) or {}
    event = {
        "type": "lead_aged",
        "lead_id": data.get("lead_id", ""),
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "service": data.get("service", ""),
        "quote_amount": data.get("quote_amount"),
        "last_contact": data.get("last_contact", ""),
        "client_id": data.get("client_id", ""),
    }
    result = dispatch("sales_consultant", event)
    return jsonify(result)


@app.route("/webhooks/uptime", methods=["POST"])
def webhook_uptime():
    """UptimeRobot alert → Website Ops"""
    data = request.get_json(force=True) or {}
    event = {
        "type": "uptime_alert",
        "monitor_url": data.get("url", ""),
        "status": data.get("alertType", ""),
        "client_id": data.get("monitorFriendlyName", ""),
    }
    result = dispatch("website_ops", event)
    return jsonify(result)


@app.route("/webhooks/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "routes": [
        "POST /webhooks/call",
        "POST /webhooks/lead",
        "POST /webhooks/job-complete",
        "POST /webhooks/lead-aged",
        "POST /webhooks/uptime",
    ]})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5051)
