"""
WebStaffr — Sales Consultant Agent
Trigger: Estimate sent / follow-up requested
Action:  Personalized follow-up email (SendGrid) + optional SMS nudge (Twilio)

Called by: POST /webhooks/estimate-followup
Body: {
    client_id, customer_name, customer_email, customer_phone,
    job_type, estimate_amount, estimate_date, follow_up_number (1|2|3)
}
"""

import os
import time
from datetime import datetime
from openai import OpenAI
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from sqlalchemy.orm import Session
from ..db import crud, models

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client  = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
sg_client      = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

TWILIO_FROM   = os.getenv("TWILIO_PHONE_NUMBER")
FROM_EMAIL    = os.getenv("SENDGRID_FROM_EMAIL", "hello@webstaffr.com")
FROM_NAME     = os.getenv("SENDGRID_FROM_NAME", "WebStaffr")


# ── Prompt templates by follow-up number ─────────────────────────────────────

EMAIL_PROMPTS = {
    1: """You are the sales consultant for a home service contractor.
A customer received an estimate and hasn't responded yet. Write a short, warm
follow-up email (3 paragraphs max) that:
1. References the specific job type and estimate they received
2. Answers the most common unspoken objection (is this the right price?)
3. Makes it easy to say yes — offer to answer questions or adjust scope
4. Closes with a gentle time anchor (e.g., "slots are filling up this week")
Subject line on first line labeled 'Subject:'. Sound like a real person, not a template.""",

    2: """You are the sales consultant for a home service contractor.
This is a second follow-up on an estimate the customer hasn't responded to.
Write a brief, direct email (2 paragraphs) that:
1. Acknowledges they're probably busy — no guilt
2. Offers something concrete: a quick call, a revised scope, or a firm hold on scheduling
3. Gives them an easy out if the timing isn't right
Subject line on first line labeled 'Subject:'. Keep it under 100 words in the body.""",

    3: """You are the sales consultant for a home service contractor.
This is a final follow-up on an estimate. Write a very short "closing the loop" email
(1 paragraph) that:
1. Says you're releasing their hold on the schedule
2. Leaves the door genuinely open — no pressure, no guilt
3. Makes it easy to come back when they're ready
Subject line on first line labeled 'Subject:'. Under 60 words. Warm, not desperate.""",
}

SMS_PROMPTS = {
    1: """Write a single SMS (under 140 chars) from a home service contractor following up
on a sent estimate. Reference the job type. Ask if they have questions. Sound human.""",

    2: """Write a brief SMS (under 140 chars) — second follow-up on an estimate that hasn't
been responded to. Offer a quick call to answer questions. No pressure.""",
}


# ── Core handler ──────────────────────────────────────────────────────────────

def handle_estimate_followup(
    db: Session,
    client_id: str,
    client: models.Client,
    customer_name: str,
    customer_email: str | None,
    customer_phone: str | None,
    job_type: str,
    estimate_amount: float | None,
    estimate_date: str | None,
    follow_up_number: int = 1,
) -> dict:
    """
    Main handler — sends a follow-up email and/or SMS on an outstanding estimate.
    follow_up_number: 1 (first nudge), 2 (second nudge), 3 (close the loop)
    """
    start = time.time()
    results = {
        "email_sent": False,
        "sms_sent": False,
        "follow_up_number": follow_up_number,
        "errors": [],
    }

    amount_str = f"${estimate_amount:,.0f}" if estimate_amount else "your estimate"
    date_str   = estimate_date or "recently"

    context = (
        f"Business: {client.biz_name}\n"
        f"Customer name: {customer_name}\n"
        f"Job type: {job_type}\n"
        f"Estimate amount: {amount_str}\n"
        f"Estimate sent: {date_str}\n"
        f"Follow-up number: {follow_up_number} of 3"
    )

    # ── Email follow-up ───────────────────────────────────────────────────────
    if customer_email and follow_up_number in EMAIL_PROMPTS:
        try:
            email_resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=350,
                messages=[
                    {"role": "system", "content": EMAIL_PROMPTS[follow_up_number]},
                    {"role": "user",   "content": context},
                ]
            )
            raw = email_resp.choices[0].message.content.strip()
            lines = raw.split("\n")
            subject = next(
                (l.replace("Subject:", "").strip() for l in lines if l.startswith("Subject:")),
                f"Following up on your {job_type} estimate — {client.biz_name}"
            )
            body = "\n".join(l for l in lines if not l.startswith("Subject:")).strip()

            message = Mail(
                from_email=(FROM_EMAIL, FROM_NAME),
                to_emails=To(customer_email, customer_name),
                subject=subject,
                plain_text_content=body,
            )
            sg_client.send(message)
            results["email_sent"]    = True
            results["email_subject"] = subject
        except Exception as e:
            results["errors"].append(f"Email: {e}")

    # ── SMS nudge (follow-ups 1 and 2 only) ───────────────────────────────────
    if customer_phone and follow_up_number in SMS_PROMPTS:
        try:
            sms_resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=80,
                messages=[
                    {"role": "system", "content": SMS_PROMPTS[follow_up_number]},
                    {"role": "user",   "content": context},
                ]
            )
            sms_body = sms_resp.choices[0].message.content.strip()[:160]
            twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_FROM,
                to=customer_phone,
            )
            results["sms_sent"] = True
            results["sms_body"] = sms_body
        except Exception as e:
            results["errors"].append(f"SMS: {e}")

    duration_ms = int((time.time() - start) * 1000)

    crud.log_agent_event(
        db=db,
        client_id=client_id,
        event_type=models.AgentEventType.estimate_followup,
        agent_name="Sales Consultant",
        input_data={
            "customer_name":   customer_name,
            "customer_email":  customer_email,
            "customer_phone":  customer_phone,
            "job_type":        job_type,
            "estimate_amount": estimate_amount,
            "follow_up_number": follow_up_number,
        },
        output_data=results,
        success=(results["email_sent"] or results["sms_sent"]),
        error_message="; ".join(results["errors"]) or None,
        duration_ms=duration_ms,
    )

    return results
