"""
WebStaffr — AI Receptionist Agent
Trigger: Twilio missed-call webhook
Action:  Send personalized SMS callback + log lead
"""

import os
import time
from openai import OpenAI
from twilio.rest import Client as TwilioClient
from sqlalchemy.orm import Session
from ..db import crud, models

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = TwilioClient(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN"),
)
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")


SYSTEM_PROMPT = """You are a friendly, professional receptionist for a home service contractor.
A customer just called and nobody answered. Write a SHORT, warm SMS text message (under 160 characters)
that:
1. Apologizes for missing their call
2. Assures them someone will call back within minutes
3. Offers to schedule via text if convenient

Be natural, not robotic. Use the business name provided. No emojis unless it fits the brand."""


def handle_missed_call(
    db: Session,
    client_id: str,
    caller_phone: str,
    client: models.Client,
) -> dict:
    """
    Main handler — called by the /webhooks/missed-call route.
    Returns a result dict for logging.
    """
    start = time.time()

    # 1. Create a lead record immediately
    lead = crud.create_lead(db, client_id, {
        "phone": caller_phone,
        "source": "missed_call",
        "name": "Unknown (missed call)",
    })

    # 2. Generate personalized SMS with OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=100,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Business name: {client.biz_name}. Customer called from {caller_phone}."},
            ]
        )
        sms_body = response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback message if OpenAI fails — never leave the customer cold
        sms_body = (
            f"Hi! You just called {client.biz_name}. Sorry we missed you — "
            "we'll call right back. Reply with your question to get started!"
        )

    # 3. Send SMS via Twilio
    sms_sent = False
    sms_error = None
    try:
        twilio_client.messages.create(
            body=sms_body,
            from_=TWILIO_FROM,
            to=caller_phone,
        )
        sms_sent = True
        crud.update_lead_status(db, lead.id, models.LeadStatus.contacted, contacted_at=__import__("datetime").datetime.utcnow())
    except Exception as e:
        sms_error = str(e)

    duration_ms = int((time.time() - start) * 1000)

    # 4. Log the agent event
    crud.log_agent_event(
        db=db,
        client_id=client_id,
        lead_id=lead.id,
        event_type=models.AgentEventType.missed_call,
        agent_name="Receptionist",
        input_data={"caller_phone": caller_phone},
        output_data={"sms_body": sms_body, "sms_sent": sms_sent},
        success=sms_sent,
        error_message=sms_error,
        duration_ms=duration_ms,
    )

    return {
        "lead_id": lead.id,
        "sms_sent": sms_sent,
        "message": sms_body,
        "error": sms_error,
    }


def generate_twiml_response(client_biz_name: str) -> str:
    """
    TwiML to play when someone calls — tells caller a text is on the way.
    Returns raw XML string.
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">
        Thank you for calling {client_biz_name}.
        We're helping another customer right now.
        We're sending you a text message right now and will call you back shortly.
        Have a great day!
    </Say>
</Response>"""
