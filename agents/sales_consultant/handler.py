"""
WebStaff Agent: Sales Consultant
Dept: Sales | Plans: growth, pro
Trigger: Lead aged > 48h with no booking; or upsell flag from CRM
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sales follow-up for a home service business. Lead requested a quote 48h ago, hasn't booked. Write a friendly, non-pushy SMS that re-opens the conversation with one concrete next step. Never pressure."""


def handle(event: dict) -> dict:
    """
    Handle a Sales Consultant event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Sales Consultant triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Twilio SMS, OpenAI GPT-4o, CRM read/write)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Sales Consultant not yet implemented — see agents/sales_consultant/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "sales_consultant", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
