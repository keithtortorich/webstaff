"""
WebStaffr CRUD helpers — thin layer over SQLAlchemy
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Client, Lead, AgentEvent, ReviewRequest, LeadStatus, AgentEventType


# ── Clients ──────────────────────────────────────────────────────────────────

def create_client(db: Session, data: dict) -> Client:
    client = Client(
        id=data.get("id", str(uuid.uuid4())),
        biz_name=data["biz_name"],
        phone=data["phone"],
        email=data["email"],
        industry=data.get("industry", "Contractor"),
        service_area=data.get("service_area"),
        site_url=data.get("site_url"),
        plan=data.get("plan", "growth"),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: str) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def get_all_clients(db: Session) -> list[Client]:
    return db.query(Client).filter(Client.active == True).all()


def get_client_by_phone(db: Session, phone: str) -> Client | None:
    """Find a client by their Twilio phone — used in webhook routing."""
    clean = "".join(c for c in phone if c.isdigit() or c == "+")
    return db.query(Client).filter(Client.phone.contains(clean[-10:])).first()


# ── Leads ────────────────────────────────────────────────────────────────────

def create_lead(db: Session, client_id: str, data: dict) -> Lead:
    lead = Lead(
        id=str(uuid.uuid4()),
        client_id=client_id,
        name=data.get("name"),
        phone=data.get("phone"),
        email=data.get("email"),
        message=data.get("message"),
        source=data.get("source", "form"),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def update_lead_status(db: Session, lead_id: str, status: LeadStatus, **kwargs) -> Lead | None:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
    lead.status = status
    for k, v in kwargs.items():
        if hasattr(lead, k):
            setattr(lead, k, v)
    db.commit()
    db.refresh(lead)
    return lead


def get_leads_for_client(db: Session, client_id: str, limit: int = 50) -> list[Lead]:
    return (
        db.query(Lead)
        .filter(Lead.client_id == client_id)
        .order_by(Lead.created_at.desc())
        .limit(limit)
        .all()
    )


# ── Agent Events ─────────────────────────────────────────────────────────────

def log_agent_event(
    db: Session,
    client_id: str,
    event_type: AgentEventType,
    agent_name: str,
    input_data: dict,
    output_data: dict,
    success: bool = True,
    error_message: str = None,
    lead_id: str = None,
    duration_ms: int = None,
) -> AgentEvent:
    event = AgentEvent(
        id=str(uuid.uuid4()),
        client_id=client_id,
        lead_id=lead_id,
        event_type=event_type,
        agent_name=agent_name,
        input_data=input_data,
        output_data=output_data,
        success=success,
        error_message=error_message,
        duration_ms=duration_ms,
    )
    db.add(event)
    db.commit()
    return event


def get_recent_events(db: Session, client_id: str, limit: int = 20) -> list[AgentEvent]:
    return (
        db.query(AgentEvent)
        .filter(AgentEvent.client_id == client_id)
        .order_by(AgentEvent.executed_at.desc())
        .limit(limit)
        .all()
    )


# ── Review Requests ───────────────────────────────────────────────────────────

def create_review_request(db: Session, client_id: str, customer_phone: str, customer_name: str = None) -> ReviewRequest:
    rr = ReviewRequest(
        id=str(uuid.uuid4()),
        client_id=client_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
    )
    db.add(rr)
    db.commit()
    return rr


# ── Dashboard Stats ───────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session, client_id: str) -> dict:
    total_leads = db.query(Lead).filter(Lead.client_id == client_id).count()
    booked = db.query(Lead).filter(Lead.client_id == client_id, Lead.status == LeadStatus.booked).count()
    reviews_sent = db.query(ReviewRequest).filter(ReviewRequest.client_id == client_id).count()
    agent_actions = db.query(AgentEvent).filter(AgentEvent.client_id == client_id, AgentEvent.success == True).count()

    return {
        "total_leads": total_leads,
        "booked_jobs": booked,
        "conversion_rate": round(booked / total_leads * 100, 1) if total_leads else 0,
        "review_requests_sent": reviews_sent,
        "agent_actions_taken": agent_actions,
    }
