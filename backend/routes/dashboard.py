"""
WebStaffr — Dashboard / Admin API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid, subprocess, json
from pathlib import Path
from ..db import models, crud, get_db

router = APIRouter(prefix="/api", tags=["dashboard"])


class ClientCreate(BaseModel):
    biz_name: str
    phone: str
    email: str
    industry: Optional[str] = "Contractor"
    service_area: Optional[str] = None
    site_url: Optional[str] = None
    plan: Optional[str] = "growth"


class OnboardPayload(BaseModel):
    biz_name: str
    phone: str
    email: str
    industry: Optional[str] = "Contractor"
    service_area: Optional[str] = None
    tagline: Optional[str] = None
    plan: Optional[str] = "growth"
    years_in_biz: Optional[int] = None
    license_number: Optional[str] = None
    rating_value: Optional[float] = None
    review_count: Optional[int] = None
    google_review_link: Optional[str] = None
    services: Optional[List[str]] = None
    services_raw: Optional[str] = None
    fsm: Optional[str] = None
    lead_routing: Optional[str] = None
    approver: Optional[str] = None


@router.post("/onboard")
async def onboard_client(
    payload: OnboardPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    client_id = str(uuid.uuid4())
    services = payload.services
    if not services and payload.services_raw:
        services = [s.strip() for s in payload.services_raw.split("\n") if s.strip()]

    crud.create_client(db, {
        "id": client_id,
        "biz_name": payload.biz_name,
        "phone": payload.phone,
        "email": payload.email,
        "industry": payload.industry or "Contractor",
        "service_area": payload.service_area,
        "plan": payload.plan or "growth",
    })

    intake_data = payload.model_dump()
    intake_data["id"] = client_id
    if services:
        intake_data["services"] = services

    intake_dir = Path("intake_queue")
    intake_dir.mkdir(exist_ok=True)
    intake_path = intake_dir / f"{client_id}.json"
    with open(intake_path, "w") as f:
        json.dump(intake_data, f, indent=2)

    background_tasks.add_task(_trigger_build, str(intake_path))

    return {
        "status": "queued",
        "client_id": client_id,
        "biz_name": payload.biz_name,
        "plan": payload.plan,
        "message": "Site build queued. Live within 24 hours.",
    }


def _trigger_build(intake_path: str):
    try:
        subprocess.run(
            ["python", "builder/site_generator.py", "--intake", intake_path],
            timeout=120, check=True,
        )
    except Exception as e:
        print(f"Build error for {intake_path}: {e}")


@router.post("/clients")
def register_client(body: ClientCreate, db: Session = Depends(get_db)):
    data = body.model_dump()
    data["id"] = str(uuid.uuid4())
    client = crud.create_client(db, data)
    return {"id": client.id, "biz_name": client.biz_name, "plan": client.plan}


@router.get("/clients")
def list_clients(db: Session = Depends(get_db)):
    clients = crud.get_all_clients(db)
    return [{"id": c.id, "biz_name": c.biz_name, "plan": c.plan,
             "industry": c.industry, "service_area": c.service_area,
             "onboarded_at": c.onboarded_at.isoformat() if c.onboarded_at else None,
             "servicetitan_tenant_id": c.servicetitan_tenant_id}
            for c in clients]


@router.get("/clients/{client_id}")
def get_client(client_id: str, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"id": client.id, "biz_name": client.biz_name, "phone": client.phone,
            "email": client.email, "plan": client.plan, "industry": client.industry,
            "service_area": client.service_area, "site_url": client.site_url, "active": client.active}


@router.get("/clients/{client_id}/stats")
def get_stats(client_id: str, db: Session = Depends(get_db)):
    if not crud.get_client(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.get_dashboard_stats(db, client_id)


@router.get("/clients/{client_id}/leads")
def get_leads(client_id: str, limit: int = 50, db: Session = Depends(get_db)):
    if not crud.get_client(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    leads = crud.get_leads_for_client(db, client_id, limit=limit)
    return [{"id": l.id, "name": l.name, "phone": l.phone, "email": l.email,
             "message": l.message, "source": l.source, "status": l.status,
             "created_at": l.created_at.isoformat() if l.created_at else None,
             "synced_to_st": l.synced_to_st}
            for l in leads]


@router.get("/clients/{client_id}/events")
def get_events(client_id: str, limit: int = 20, db: Session = Depends(get_db)):
    if not crud.get_client(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    events = crud.get_recent_events(db, client_id, limit=limit)
    return [{"id": e.id, "agent": e.agent_name, "type": e.event_type,
             "success": e.success,
             "executed_at": e.executed_at.isoformat() if e.executed_at else None,
             "duration_ms": e.duration_ms}
            for e in events]


@router.get("/overview")
def operator_overview(db: Session = Depends(get_db)):
    from ..db.models import Client, Lead, AgentEvent
    total_clients = db.query(Client).filter(Client.active == True).count()
    total_leads   = db.query(Lead).count()
    total_actions = db.query(AgentEvent).filter(AgentEvent.success == True).count()
    mrr_map = {"essentials": 197, "growth": 497, "pro": 997}
    clients = crud.get_all_clients(db)
    mrr = sum(mrr_map.get(c.plan, 497) for c in clients)
    return {"active_clients": total_clients, "total_leads_captured": total_leads,
            "agent_actions_executed": total_actions,
            "estimated_mrr": mrr, "estimated_arr": mrr * 12}
