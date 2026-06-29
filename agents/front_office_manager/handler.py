"""
WebStaff Agent: Front Office Manager
Dept: Operations | Plans: growth, pro
Trigger: Any inbound event — call, form, CRM update, job close
"""
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Front office manager. An event just came in. Classify it and return JSON: {event_type, agent, priority, reason}."""


def handle(event: dict) -> dict:
    """
    Handle a Front Office Manager event.

    Args:
        event: Trigger payload dict (see spec.md for schema)
    Returns:
        dict: success, output, actions_taken, timestamp
    """
    logger.info("Front Office Manager triggered", extra={"event": event.get("type")})

    # TODO: implement
    # 1. Validate event payload
    # 2. OpenAI call with SYSTEM_PROMPT + event context
    # 3. Execute tool actions (Internal routing logic, Celery task dispatch, CRM read)
    # 4. Log outcome
    # 5. Return structured result

    raise NotImplementedError(
        "Front Office Manager not yet implemented — see agents/front_office_manager/spec.md"
    )


if __name__ == "__main__":
    mock = {"type": "front_office_manager", "timestamp": datetime.now().isoformat(), "client_id": "test-001", "payload": {}}
    try:
        print(json.dumps(handle(mock), indent=2))
    except NotImplementedError as e:
        print(f"Not implemented: {e}")
