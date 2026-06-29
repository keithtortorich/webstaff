"""
WebStaffr — Lead Coordinator Agent
Trigger: New lead via website contact form
Action:  Instant personalized SMS + follow-up email sequence
"""

import os
import time
from openai import OpenAI
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from sqlalchemy.orm import Session
from ..db import crud, models

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = TwilioClient(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN"),
)
sg_client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "hello@webstaffr.com")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "WebStaffr")


SMS_SYSTEM_PROMPT = """You are the lead coordinator for a home service contractor.
A new customer just submitted a contact form. Write a SHORT SMS (under 160 chars) that:
1. Thanks them by first name (use it if provided)
2. Confirms you received their request
3. Promises fast follow-up (within the hour)
Sound human, warm, professional. No corporate-speak."""

EMAIL_SYSTEM_PROMPT = """You are the lead coordinator for a home service contractor.
Write a brief follow-up email (3 short paragraphs, no fluff) to a new lead that:
1. Thanks them for reaching out
2. Summarizes what they asked about (use their message)
3. States exactly what happens next
Sign from the business name provided. Subject line included as first line labeled 'Subject:'"""


def handle_new_lead(
    db: Session,
    client_id: str,
    lead_data: dict,
    client: models.Client,
) -> dict:
    """
    Main handler — called by /webhooks/lead-form route.
    lead_data: {name, phone, email, message, source}
    """
    start = time.time()

    # 1. Persist the lead
    lead = crud.create_lead(db, client_id, lead_data)

    results = {"lead_id": lead.id, "sms_sent": False, "email_sent": False, "errors": []}

    # 2. Send instant SMS (if phone provided)
    if lead_data.get("phone"):
        try:
            sms_resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=100,
                messages=[
                    {"role": "system", "content": SMS_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"Business: {client.biz_name}\n"
                        f"Customer name: {lead_data.get('name', 'there')}\n"
                        f"Their message: {lead_data.get('message', 'general inquiry')}"
                    )},
                ]
            )
            sms_body = sms_resp.choices[0].message.content.strip()
            twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_FROM,
                to=lead_data["phone"],
            )
            results["sms_sent"] = True
            results["sms_body"] = sms_body
        except Exception as e:
            results["errors"].append(f"SMS: {str(e)}")

    # 3. Send follow-up email (if email provided)
    if lead_data.get("email"):
        try:
            email_resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=300,
                messages=[
                    {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"Business: {client.biz_name}\n"
                        f"Customer: {lead_data.get('name', 'Customer')}\n"
                        f"Their inquiry: {lead_data.get('message', 'general inquiry')}\n"
                        f"Industry: {client.industry}"
                    )},
                ]
            )
            raw = email_resp.choices[0].message.content.strip()
            lines = raw.split("\n")
            subject = next((l.replace("Subject:", "").strip() for l in lines if l.startswith("Subject:")),
                           f"We got your message — {client.biz_name}")
            body = "\n".join(l for l in lines if not l.startswith("Subject:")).strip()

            message = Mail(
                from_email=(FROM_EMAIL, FROM_NAME),
                to_emails=To(lead_data["email"], lead_data.get("name")),
                subject=subject,
                plain_text_content=body,
            )
            sg_client.send(message)
            results["email_sent"] = True
            results["email_subject"] = subject
        except Exception as e:
            results["errors"].append(f"Email: {str(e)}")

    # 4. Update lead status
    crud.update_lead_status(
        db, lead.id, models.LeadStatus.contacted,
        contacted_at=__import__("datetime").datetime.utcnow()
    )

    duration_ms = int((time.time() - start) * 1000)

    crud.log_agent_event(
        db=db,
        client_id=client_id,
        lead_id=lead.id,
        event_type=models.AgentEventType.form_submit,
        agent_name="Lead Coordinator",
        input_data=lead_data,
        output_data=results,
        success=(results["sms_sent"] or results["email_sent"]),
        error_message="; ".join(results["errors"]) or None,
        duration_ms=duration_ms,
    )

    return results
