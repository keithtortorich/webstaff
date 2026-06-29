"""
WebStaff Agent: Front Office Manager
Celery task — calls workflows.call_agent() then fires real tool actions.
See agents/front_office_manager/spec.md for full spec.
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Import the central agent caller
try:
    from agents.workflows import call_agent
except ImportError:
    # Running standalone
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from agents.workflows import call_agent


def handle(event: dict) -> dict:
    """
    Handle a front_office_manager event.
    Replace the TODOs below with real tool calls (Twilio, GBP API, etc.)
    See agents/front_office_manager/spec.md for the full tool list and success metric.
    """
    logger.info("front_office_manager triggered", extra={"event_type": event.get("type")})

    # 1. Generate AI response
    context = event.get("payload", event)
    ai_output = call_agent(
        "front_office_manager",
        f"Handle this event: {json.dumps(context)}",
        context=context,
    )

    # 2. TODO: execute tool actions
    #    e.g. Twilio SMS, GBP API post, CRM write
    #    Uncomment and configure when integrations are ready:
    #
    #    from twilio.rest import Client
    #    twilio = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH"])
    #    twilio.messages.create(body=ai_output, from_=FROM, to=event["phone"])

    return {
        "agent":       "front_office_manager",
        "timestamp":   datetime.now().isoformat(),
        "event_type":  event.get("type", "unknown"),
        "ai_output":   ai_output,
        "tools_fired": [],   # populate when integrations are wired
        "status":      "ai_complete_tools_pending",
    }


if __name__ == "__main__":
    mock = {
        "type": "front_office_manager",
        "timestamp": datetime.now().isoformat(),
        "client_id": "test-001",
        "payload": {"name": "Test Client", "phone": "(602) 555-0100"},
    }
    import json
    print(json.dumps(handle(mock), indent=2))
