"""
WebStaff Agent Workflows
Ported from CrewAI prototype → simple FastAPI + Celery + OpenAI stack.

Decision: No CrewAI / LangChain. Reasons:
  - Every agent needs REAL tool calls (Twilio, GBP API, SendGrid) — CrewAI wraps LLM text, not APIs
  - Non-deterministic multi-agent chaining is a liability in production; Celery tasks are auditable
  - Zero additional framework dependencies; OpenAI SDK directly is 10x simpler to debug
  - See: /docs/simple_stack.md

Agent system prompts are preserved verbatim from the CrewAI prototype.
Workflows map 1:1 to Celery task chains.
"""

import os
import json
import logging
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ── Model routing ─────────────────────────────────────────────────────────────
# Match cost intent from CrewAI prototype: gpt-4o-mini for routine, gpt-4o for complex
MODELS = {
    "fast":    "gpt-4o-mini",   # receptionist, lead coord, reputation, marketing, website ops, service advisor
    "precise": "gpt-4o",        # growth manager, sales consultant, front office manager
}

# ── Agent definitions ─────────────────────────────────────────────────────────
# Role / Goal / Backstory preserved from CrewAI prototype.
# Used as system prompts in direct OpenAI calls.
AGENTS = {
    "receptionist": {
        "model": MODELS["fast"],
        "system": (
            "Role: 24/7 Receptionist. "
            "Goal: Answer every call and qualify leads instantly. "
            "You have 15 years of front desk experience at busy home service companies. "
            "You answer calls professionally, qualify the job (trade, urgency, location), "
            "collect the caller's name and phone. Speak plain English, never read from a script, "
            "always end with a confirmed next step."
        ),
    },
    "lead_coordinator": {
        "model": MODELS["fast"],
        "system": (
            "Role: Lead Coordinator. "
            "Goal: Follow up every lead and book appointments. "
            "You've been in sales operations for a decade. "
            "A customer just submitted a web form. Write a warm SMS reply acknowledging their request "
            "and asking one qualifying question. Under 160 characters."
        ),
    },
    "reputation_manager": {
        "model": MODELS["fast"],
        "system": (
            "Role: Reputation Manager. "
            "Goal: Get more 5-star reviews automatically. "
            "You've managed online reputation for 20+ businesses. "
            "Send a friendly review request using the customer's first name and the specific service. "
            "Never sound automated. Warm and genuine."
        ),
    },
    "marketing_coordinator": {
        "model": MODELS["fast"],
        "system": (
            "Role: Marketing Coordinator. "
            "Goal: Keep the business visible every day. "
            "You've been a marketing coordinator for home service brands for 8 years. "
            "Write a short engaging social post. Sound like a real local business owner, not an agency. "
            "Include a soft CTA."
        ),
    },
    "growth_manager": {
        "model": MODELS["precise"],
        "system": (
            "Role: Growth Manager. "
            "Goal: Improve search visibility and inbound leads. "
            "You've been an SEO and growth specialist for 12 years. "
            "Review this GBP data and write optimized service descriptions. "
            "Use natural language matching how customers search. Include city and trade keywords naturally."
        ),
    },
    "website_ops": {
        "model": MODELS["fast"],
        "system": (
            "Role: Website Operations Manager. "
            "Goal: Keep the site online and secure. "
            "You've been a DevOps engineer for 15 years. "
            "Write a plain-English 3-4 sentence health summary for the business owner: "
            "uptime, speed, issues, what was fixed."
        ),
    },
    "sales_consultant": {
        "model": MODELS["precise"],
        "system": (
            "Role: Sales Consultant. "
            "Goal: Help customers say yes to bigger jobs. "
            "You've been selling home services for 20 years. "
            "A lead requested a quote 48h ago and hasn't booked. Write a friendly, non-pushy SMS "
            "that re-opens the conversation with one concrete next step. Never pressure."
        ),
    },
    "service_advisor": {
        "model": MODELS["fast"],
        "system": (
            "Role: Service Advisor. "
            "Goal: Pre-qualify customers and capture details. "
            "You've been a dispatcher and service advisor for 12 years. "
            "Ask 3-4 targeted questions: issue, urgency, property type, location. "
            "Be efficient and professional. Output a structured job brief."
        ),
    },
    "front_office_manager": {
        "model": MODELS["precise"],
        "system": (
            "Role: Front Office Manager. "
            "Goal: Coordinate all AI employees. "
            "You've run operations for fast-growing service businesses for 15 years. "
            "An event just came in. Classify it and return JSON only: "
            "{\"event_type\": str, \"agent\": str, \"priority\": \"high|normal|low\", \"reason\": str}"
        ),
    },
}


def call_agent(agent_slug: str, user_message: str, context: dict = None) -> str:
    """
    Direct OpenAI call for any agent. No framework wrapper.

    Args:
        agent_slug:   Key from AGENTS dict
        user_message: The task/prompt specific to this event
        context:      Optional dict merged into user message as JSON context

    Returns:
        Agent response string
    """
    agent = AGENTS[agent_slug]
    if not agent:
        raise ValueError(f"Unknown agent: {agent_slug}")

    messages = [{"role": "system", "content": agent["system"]}]

    if context:
        user_message = f"{user_message}\n\nContext: {json.dumps(context, indent=2)}"

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=agent["model"],
        messages=messages,
        temperature=0.3,
    )

    result = response.choices[0].message.content
    logger.info("agent_call", extra={
        "agent": agent_slug,
        "model": agent["model"],
        "tokens": response.usage.total_tokens,
    })
    return result


# ── Workflows ─────────────────────────────────────────────────────────────────
# These mirror the CrewAI sequential workflow but as plain Python functions.
# In production: each step is a Celery task; the chain runs async.
# For now: synchronous for testing — replace with .delay() calls when Celery is wired.

def lead_to_booked_workflow(lead_data: dict) -> dict:
    """
    Main end-to-end workflow: inbound lead → qualified → followed up → (post-job) → review.
    Mirrors CrewAI prototype's lead_to_booked_workflow().

    Steps:
      1. Receptionist  — qualify the lead
      2. LeadCoordinator — draft follow-up SMS
      3. ReputationManager — draft review request (queued for post-job send)
    """
    results = {}
    timestamp = datetime.now().isoformat()

    # Step 1 — Qualify
    results["qualification"] = call_agent(
        "receptionist",
        f"New lead came in. Qualify and summarize: {json.dumps(lead_data)}",
        context=lead_data,
    )

    # Step 2 — Follow-up SMS
    results["followup_sms"] = call_agent(
        "lead_coordinator",
        "Draft a follow-up SMS for this lead.",
        context={**lead_data, "qualification": results["qualification"]},
    )

    # Step 3 — Review request (staged for post-job)
    results["review_request_draft"] = call_agent(
        "reputation_manager",
        "Draft a review request SMS for after the job is complete.",
        context=lead_data,
    )

    return {
        "workflow": "lead_to_booked",
        "timestamp": timestamp,
        "lead": lead_data,
        "steps": results,
        "status": "complete",
    }


def route_event(event: dict) -> dict:
    """
    Front Office Manager classifies any inbound event and returns routing decision.
    Replaces CrewAI's hierarchical process manager.
    """
    raw = call_agent(
        "front_office_manager",
        f"Classify this event and return routing JSON: {json.dumps(event)}",
    )
    try:
        routing = json.loads(raw)
    except json.JSONDecodeError:
        routing = {"event_type": "unknown", "agent": "front_office_manager",
                   "priority": "normal", "reason": raw}
    return routing


# ── Smoke test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Mirrors the __main__ block from the CrewAI prototype
    lead = {
        "name": "John",
        "issue": "Emergency plumbing",
        "city": "Phoenix",
        "phone": "(602) 555-0100",
        "source": "website_form",
    }

    print("Running lead_to_booked_workflow...\n")
    result = lead_to_booked_workflow(lead)
    print(json.dumps(result, indent=2))
