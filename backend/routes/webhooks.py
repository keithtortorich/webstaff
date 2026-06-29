"""
WebStaffr — Inbound Webhook Routes
Handles: Twilio voice/SMS + website lead form submissions
"""

from fastapi import APIRouter, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from ..db import models, crud, get_db
from ..agents import receptionist, lead_coordinator, reputation_manager
from .integrations import sync_lead

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# ── Twilio: Incoming Call ────────────────────────────────────────────────────

@router.post("/voice/incoming")
async def voice_incoming(
    request: Request,
    background_tasks: BackgroundTasks,
    To: str = Form(...),        # The client's Twilio number (routes to correct client)
    From: str = Form(...),      # Caller's number
    db: Session = Depends(get_db),
):
    """
    Twilio calls this URL when a call comes in to a client's number.
    Returns TwiML immediately, fires missed-call SMS handler in background.
    """
    client = crud.get_client_by_phone(db, To)
    if not client:
        # Generic fallback — unknown number
        twiml = """<?xml version="1.0"?><Response><Say>Thank you for calling. Please try again shortly.</Say></Response>"""
        return Response(content=twiml, media_type="application/xml")

    # Queue the SMS handler as a background task (don't block TwiML response)
    background_tasks.add_task(
        receptionist.handle_missed_call,
        db=db,
        client_id=client.id,
        caller_phone=From,
        client=client,
    )

    twiml = receptionist.generate_twiml_response(client.biz_name)
    return Response(content=twiml, media_type="application/xml")


# ── Website Lead Form ────────────────────────────────────────────────────────

@router.post("/lead-form")
async def lead_form_submit(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Receives lead form submissions from client websites.
    Expected JSON body: {client_id, name, phone, email, message}
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON body required")

    client_id = body.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")

    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    lead_data = {
        "name": body.get("name"),
        "phone": body.get("phone"),
        "email": body.get("email"),
        "message": body.get("message"),
        "source": "form",
    }

    # Fire Lead Coordinator in background
    background_tasks.add_task(
        lead_coordinator.handle_new_lead,
        db=db,
        client_id=client_id,
        lead_data=lead_data,
        client=client,
    )

    # Also push to ServiceTitan (Phase 1: Zapier, Phase 2: native)
    background_tasks.add_task(_st_sync_after_lead_create, db, client_id, lead_data, client)

    return JSONResponse({"status": "received", "message": "We'll be in touch shortly!"})


async def _st_sync_after_lead_create(db, client_id, lead_data, client):
    """Helper: create lead then sync to ST. Runs in background."""
    # Lead may already be created by lead_coordinator — find by phone
    import asyncio
    await asyncio.sleep(2)  # Small delay to let lead_coordinator commit first
    leads = crud.get_leads_for_client(db, client_id, limit=1)
    if leads:
        await sync_lead(db, leads[0], client)


# ── Job Complete (ServiceTitan webhook or manual) ────────────────────────────

@router.post("/job-complete")
async def job_complete(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Called when a job is marked complete.
    Triggers: Reputation Manager sends review request.
    Can be called manually by operator or by ServiceTitan webhook (Phase 2).
    
    Body: {client_id, customer_phone, customer_name, job_type, google_review_link}
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON body required")

    client_id = body.get("client_id")
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    background_tasks.add_task(
        reputation_manager.request_review,
        db=db,
        client_id=client_id,
        customer_phone=body["customer_phone"],
        customer_name=body.get("customer_name", "Valued Customer"),
        job_type=body.get("job_type", client.industry),
        google_review_link=body.get("google_review_link", "https://g.page/r/your-review-link"),
        client=client,
    )

    return JSONResponse({"status": "review_request_queued"})
