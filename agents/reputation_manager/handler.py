"""
WebStaff Agent: Reputation Manager
Dept: Marketing | Plans: growth, pro
Trigger: Job-complete event from CRM webhook
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sending a friendly review request on behalf of a contractor. Use customer first name, mention the specific service. Never sound automated. Warm and genuine."""


def handle(event: dict) -> dict:
    """
    Handle a Reputation Manager event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Reputation Manager triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Twilio SMS, OpenAI GPT-4o, GBP API)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Reputation Manager not yet implemented — see agents/reputation_manager/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "reputation_manager", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
