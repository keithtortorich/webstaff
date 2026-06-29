"""
WebStaff Agent: Service Advisor
Dept: Sales | Plans: pro
Trigger: Inbound call or SMS — parallel to Receptionist
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Service dispatcher for a home service company. Ask 3-4 targeted questions: issue, urgency, property type, location. Be efficient and professional. Output a structured job brief."""


def handle(event: dict) -> dict:
    """
    Handle a Service Advisor event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Service Advisor triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Twilio Voice/SMS, OpenAI GPT-4o, Google Maps API)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Service Advisor not yet implemented — see agents/service_advisor/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "service_advisor", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
