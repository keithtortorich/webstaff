"""
WebStaff Agent: Marketing Coordinator
Dept: Marketing | Plans: pro
Trigger: Weekly cron — Monday 9am client timezone
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Social media coordinator for a home service business. Write a short engaging Facebook post. Sound like a real local business owner, not an agency. Include a soft CTA."""


def handle(event: dict) -> dict:
    """
    Handle a Marketing Coordinator event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Marketing Coordinator triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Meta Graph API, Google Business API, OpenAI GPT-4o, Unsplash API)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Marketing Coordinator not yet implemented — see agents/marketing_coordinator/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "marketing_coordinator", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
