"""
WebStaffr — Reputation Manager Agent
Trigger: Job complete event (manual API call or ServiceTitan webhook)
Action:  Send personalized review request SMS with Google Business link
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


REVIEW_SYSTEM_PROMPT = """You are the reputation manager for a home service contractor.
A technician just completed a job. Write a SHORT, warm SMS (under 160 chars including the link placeholder) that:
1. Thanks the customer by name (use it)
2. Mentions the specific job type if provided
3. Asks them to leave a quick Google review
4. Ends with: [REVIEW_LINK]

Be genuine, not salesy. The customer just spent money — make them feel valued."""


def request_review(
    db: Session,
    client_id: str,
    customer_phone: str,
    customer_name: str,
    job_type: str,
    google_review_link: str,
    client: models.Client,
) -> dict:
    """
    Sends a post-job review request SMS.
    Called manually or by ServiceTitan job-complete webhook.
    """
    start = time.time()

    # Generate personalized message
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=120,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Business: {client.biz_name}\n"
                    f"Customer: {customer_name}\n"
                    f"Job type: {job_type or 'service call'}"
                )},
            ]
        )
        sms_body = response.choices[0].message.content.strip()
        sms_body = sms_body.replace("[REVIEW_LINK]", google_review_link)
    except Exception:
        sms_body = (
            f"Hi {customer_name}! Thanks for choosing {client.biz_name}. "
            f"If we did a great job today, we'd love a quick Google review: {google_review_link}"
        )

    # Send SMS
    sms_sent = False
    error = None
    try:
        twilio_client.messages.create(
            body=sms_body[:320],  # Stay under MMS threshold
            from_=TWILIO_FROM,
            to=customer_phone,
        )
        sms_sent = True
        crud.create_review_request(db, client_id, customer_phone, customer_name)
    except Exception as e:
        error = str(e)

    duration_ms = int((time.time() - start) * 1000)

    crud.log_agent_event(
        db=db,
        client_id=client_id,
        event_type=models.AgentEventType.review_request,
        agent_name="Reputation Manager",
        input_data={
            "customer_phone": customer_phone,
            "customer_name": customer_name,
            "job_type": job_type,
        },
        output_data={"sms_body": sms_body, "sms_sent": sms_sent},
        success=sms_sent,
        error_message=error,
        duration_ms=duration_ms,
    )

    return {"sms_sent": sms_sent, "message": sms_body, "error": error}
