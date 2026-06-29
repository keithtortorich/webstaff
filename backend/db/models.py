"""
WebStaffr Database Models
SQLAlchemy ORM — SQLite (dev) / Postgres (production)
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Float,
    Boolean, DateTime, Text, Enum as SAEnum, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.sqlite import JSON
import os
import enum

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./webstaffr.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Enums ────────────────────────────────────────────────────────────────────

class PlanTier(str, enum.Enum):
    essentials = "essentials"        # $197/mo
    growth = "growth"                # $497/mo
    pro = "pro"                      # $997/mo


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    booked = "booked"
    lost = "lost"


class AgentEventType(str, enum.Enum):
    missed_call = "missed_call"
    form_submit = "form_submit"
    review_request = "review_request"
    estimate_followup = "estimate_followup"
    job_complete = "job_complete"


# ── Models ───────────────────────────────────────────────────────────────────

class Client(Base):
    """A contractor subscribed to WebStaffr."""
    __tablename__ = "clients"

    id = Column(String, primary_key=True)               # uuid
    biz_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    industry = Column(String, default="Contractor")
    service_area = Column(String)
    site_url = Column(String)                           # Their WebStaffr-built site
    plan = Column(SAEnum(PlanTier), default=PlanTier.growth)
    active = Column(Boolean, default=True)
    onboarded_at = Column(DateTime, default=datetime.utcnow)
    stripe_customer_id = Column(String)                 # Phase 2: billing
    servicetitan_tenant_id = Column(String)             # Phase 2: ST integration

    leads = relationship("Lead", back_populates="client", cascade="all, delete")
    events = relationship("AgentEvent", back_populates="client", cascade="all, delete")

    def __repr__(self):
        return f"<Client {self.biz_name} [{self.plan}]>"


class Lead(Base):
    """An inbound lead captured via client website or Twilio."""
    __tablename__ = "leads"

    id = Column(String, primary_key=True)               # uuid
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    message = Column(Text)
    source = Column(String)                             # form | missed_call | chat
    status = Column(SAEnum(LeadStatus), default=LeadStatus.new)
    created_at = Column(DateTime, default=datetime.utcnow)
    contacted_at = Column(DateTime)
    booked_at = Column(DateTime)

    # ServiceTitan sync (Phase 2)
    servicetitan_job_id = Column(String)
    servicetitan_customer_id = Column(String)
    synced_to_st = Column(Boolean, default=False)

    client = relationship("Client", back_populates="leads")

    def __repr__(self):
        return f"<Lead {self.name} → {self.status}>"


class AgentEvent(Base):
    """Audit log of every AI agent action."""
    __tablename__ = "agent_events"

    id = Column(String, primary_key=True)               # uuid
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    event_type = Column(SAEnum(AgentEventType), nullable=False)
    agent_name = Column(String)                         # "Receptionist", "Lead Coordinator", etc.
    input_data = Column(JSON)                           # Raw trigger payload
    output_data = Column(JSON)                          # What the agent did
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer)

    client = relationship("Client", back_populates="events")

    def __repr__(self):
        return f"<AgentEvent {self.agent_name} [{self.event_type}]>"


class ReviewRequest(Base):
    """Tracks review requests sent by Reputation Manager."""
    __tablename__ = "review_requests"

    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_name = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    review_received = Column(Boolean, default=False)
    review_rating = Column(Integer)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call once at startup."""
    Base.metadata.create_all(bind=engine)
