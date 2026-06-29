"""
WebStaff Agent: Lead Coordinator
Dept: Front Office | Plans: growth, pro
Trigger: Form submission webhook from client site /api/leads
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Lead coordinator for a home service business. A customer just submitted a web form. Write a warm SMS reply that acknowledges their request and asks one qualifying question. Under 160 characters."""


def handle(event: dict) -> dict:
    """
    Handle a Lead Coordinator event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Lead Coordinator triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Twilio SMS, OpenAI GPT-4o, CRM write)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Lead Coordinator not yet implemented — see agents/lead_coordinator/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "lead_coordinator", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
