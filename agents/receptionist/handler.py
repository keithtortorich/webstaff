"""
WebStaff Agent: Receptionist
Dept: Front Office | Plans: growth, pro
Trigger: Inbound call (Twilio webhook)
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Senior receptionist at a busy home service company. Answer calls professionally, qualify the job (trade, urgency, location), collect caller name and phone. Speak plain English, never read from a script, always end with a confirmed next step."""


def handle(event: dict) -> dict:
    """
    Handle a Receptionist event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Receptionist triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Twilio Voice, OpenAI GPT-4o, CRM write)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Receptionist not yet implemented — see agents/receptionist/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "receptionist", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
