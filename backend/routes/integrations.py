"""
WebStaffr — Platform Integration Layer
========================================
Handles all FSM integrations through a common interface.

Active:
  - ServiceTitan Phase 1 (Zapier bridge)

Stubbed and ready:
  - ServiceTitan Phase 2 (native OAuth API)
  - ServiceTitan Phase 3 (AI context / customer history)
  - Jobber (Phase 2)
  - Housecall Pro (Phase 2)
  - Google Calendar (Phase 2)

Investor framing:
    "We want ServiceTitan to build AI features — it validates the category.
     We're the specialized front-office layer that benefits from their distribution."
"""

import os
import asyncio
import httpx
from sqlalchemy.orm import Session
from ..db import crud, models


# ── Constants ─────────────────────────────────────────────────────────────────

# ServiceTitan
ST_API_BASE = os.getenv("ST_API_BASE", "https://api.servicetitan.io")
ST_AUTH_URL = "https://auth.servicetitan.io/connect/token"
ST_CLIENT_ID = os.getenv("ST_CLIENT_ID")
ST_CLIENT_SECRET = os.getenv("ST_CLIENT_SECRET")
ST_TENANT_ID = os.getenv("ST_TENANT_ID")

# Jobber (Phase 2)
JOBBER_CLIENT_ID = os.getenv("JOBBER_CLIENT_ID")
JOBBER_CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET")
JOBBER_API_BASE = "https://api.getjobber.com/api/graphql"

# Housecall Pro (Phase 2)
HCP_API_KEY = os.getenv("HCP_API_KEY")
HCP_API_BASE = "https://api.housecallpro.com"

# Zapier Phase 1 bridge (no FSM credentials required)
ZAPIER_ST_WEBHOOK = os.getenv("ZAPIER_SERVICETITAN_WEBHOOK_URL")
ZAPIER_JOBBER_WEBHOOK = os.getenv("ZAPIER_JOBBER_WEBHOOK_URL")
ZAPIER_HCP_WEBHOOK = os.getenv("ZAPIER_HCP_WEBHOOK_URL")


# ── FSM Detection ─────────────────────────────────────────────────────────────

def detect_fsm(client: models.Client) -> str | None:
    """
    Returns the FSM platform in use for this client, or None.
    Priority: ST > Jobber > HCP > None.
    """
    if client.servicetitan_tenant_id:
        return "servicetitan"
    # Phase 2: add jobber_account_id, hcp_company_id fields to Client model
    return None


# ── Master Sync Entry Point ───────────────────────────────────────────────────

async def sync_lead(db: Session, lead: models.Lead, client: models.Client) -> dict:
    """
    Routes lead sync to the correct FSM integration.
    Falls back to Zapier bridge when no native credentials are configured.
    """
    fsm = detect_fsm(client)

    if fsm == "servicetitan":
        if ST_CLIENT_ID and ST_CLIENT_SECRET and ST_TENANT_ID:
            return await _st_native_sync(db, lead, client)
        elif ZAPIER_ST_WEBHOOK:
            return await _zapier_sync(ZAPIER_ST_WEBHOOK, lead, client, "servicetitan")

    elif fsm == "jobber":
        if JOBBER_CLIENT_ID and ZAPIER_JOBBER_WEBHOOK:
            return await _zapier_sync(ZAPIER_JOBBER_WEBHOOK, lead, client, "jobber")

    elif fsm == "housecallpro":
        if HCP_API_KEY and ZAPIER_HCP_WEBHOOK:
            return await _zapier_sync(ZAPIER_HCP_WEBHOOK, lead, client, "housecallpro")

    # No FSM configured — log and return
    return {"synced": False, "reason": "no_fsm_configured"}


# ── Phase 1: Zapier Bridge ────────────────────────────────────────────────────

async def _zapier_sync(webhook_url: str, lead: models.Lead, client: models.Client, platform: str) -> dict:
    """
    Universal Zapier bridge — same payload schema regardless of FSM.
    Zapier Zap maps fields to the target platform's API.

    Setup (5 min):
      1. Zapier → New Zap → Catch Hook (copy URL → .env)
      2. Action → [ServiceTitan | Jobber | HCP] → Create Customer + Create Job
      3. Map fields from payload below
    """
    payload = {
        # Customer fields
        "customer_name": lead.name or "Unknown",
        "customer_phone": lead.phone,
        "customer_email": lead.email,
        "customer_message": lead.message,

        # Job fields
        "job_type": client.industry,
        "job_source": "WebStaffr",
        "job_notes": f"AI-captured lead. Source: {lead.source}. Lead ID: {lead.id}",
        "business_unit": client.biz_name,
        "service_area": client.service_area,

        # Meta (for FSM deduplication and WebStaffr audit)
        "webstaffr_lead_id": lead.id,
        "webstaffr_client_id": lead.client_id,
        "platform": platform,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            resp = await http.post(webhook_url, json=payload)
        success = resp.status_code < 400
        if success:
            crud.update_lead_status(lead.client_id, lead.id, models.LeadStatus.contacted, synced_to_st=True)
        return {"synced": success, "platform": platform, "status": resp.status_code}
    except Exception as e:
        return {"synced": False, "platform": platform, "error": str(e)}


# ── Phase 2: ServiceTitan Native API ─────────────────────────────────────────

_st_token_cache: dict = {"token": None, "expires_at": 0}


async def _get_st_token() -> str:
    """OAuth2 client credentials — ServiceTitan auth.servicetitan.io."""
    import time
    if _st_token_cache["token"] and time.time() < _st_token_cache["expires_at"] - 60:
        return _st_token_cache["token"]

    async with httpx.AsyncClient() as http:
        resp = await http.post(ST_AUTH_URL, data={
            "grant_type": "client_credentials",
            "client_id": ST_CLIENT_ID,
            "client_secret": ST_CLIENT_SECRET,
        })
        resp.raise_for_status()
        data = resp.json()
        _st_token_cache["token"] = data["access_token"]
        _st_token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
        return data["access_token"]


async def _st_native_sync(db: Session, lead: models.Lead, client: models.Client) -> dict:
    """
    Phase 2: Bidirectional native ServiceTitan sync.
    Creates/updates Customer + Job. Attaches AI conversation summary.
    """
    token = await _get_st_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "ST-App-Key": ST_CLIENT_ID,
    }
    base = f"{ST_API_BASE}/crm/v2/tenant/{ST_TENANT_ID}"

    async with httpx.AsyncClient(timeout=15.0) as http:
        # 1. Check for existing customer (deduplication)
        existing = None
        if lead.phone:
            search = await http.get(f"{base}/customers", headers=headers, params={"phoneNumber": lead.phone})
            results = search.json().get("data", [])
            if results:
                existing = results[0]

        # 2. Create or update customer
        customer_payload = {
            "name": lead.name or "Unknown",
            "type": "Residential",
            "contacts": [
                {"type": "Phone", "value": lead.phone, "memo": "Primary"},
                {"type": "Email", "value": lead.email, "memo": "Primary"},
            ],
        }
        if existing:
            cust_resp = await http.patch(f"{base}/customers/{existing['id']}", headers=headers, json=customer_payload)
            customer_id = existing["id"]
        else:
            cust_resp = await http.post(f"{base}/customers", headers=headers, json=customer_payload)
            customer_id = cust_resp.json().get("id")

        # 3. Create job
        job_payload = {
            "customerId": customer_id,
            "summary": f"WebStaffr AI Lead — {client.industry}",
            "jobTypeId": None,  # Phase 2: map to ST job type IDs
            "source": "WebStaffr",
            "externalId": lead.id,
            "tags": ["webstaffr", client.industry.lower()],
            "customFields": [
                {"typeId": "webstaffr_lead_id", "value": lead.id},
                {"typeId": "ai_summary", "value": lead.message or ""},
            ],
        }
        job_base = f"{ST_API_BASE}/jpm/v2/tenant/{ST_TENANT_ID}"
        job_resp = await http.post(f"{job_base}/jobs", headers=headers, json=job_payload)
        job_id = job_resp.json().get("id")

    if customer_id and job_id:
        crud.update_lead_status(
            db, lead.id, models.LeadStatus.contacted,
            servicetitan_customer_id=str(customer_id),
            servicetitan_job_id=str(job_id),
            synced_to_st=True,
        )
        return {"synced": True, "platform": "servicetitan", "customer_id": customer_id, "job_id": job_id}

    return {"synced": False, "platform": "servicetitan", "error": "Missing ID in ST response"}


# ── Phase 3: AI Context Layer ─────────────────────────────────────────────────

async def get_customer_context(phone: str, client: models.Client) -> dict | None:
    """
    Phase 3: Pulls customer history from ServiceTitan before an AI conversation.
    Enables: "Welcome back Mike — your condenser is still under warranty."

    Returns a context dict that is injected into the AI receptionist system prompt.
    Returns None if no history found or ST not configured.
    """
    if not (ST_CLIENT_ID and ST_CLIENT_SECRET and ST_TENANT_ID):
        return None  # Phase 2 required first

    try:
        token = await _get_st_token()
        headers = {"Authorization": f"Bearer {token}", "ST-App-Key": ST_CLIENT_ID}
        base = f"{ST_API_BASE}/crm/v2/tenant/{ST_TENANT_ID}"

        async with httpx.AsyncClient(timeout=10.0) as http:
            search = await http.get(f"{base}/customers", headers=headers, params={"phoneNumber": phone})
            customers = search.json().get("data", [])
            if not customers:
                return None

            customer = customers[0]
            customer_id = customer["id"]

            # Pull job history
            job_base = f"{ST_API_BASE}/jpm/v2/tenant/{ST_TENANT_ID}"
            jobs_resp = await http.get(
                f"{job_base}/jobs",
                headers=headers,
                params={"customerId": customer_id, "active": "true", "pageSize": 5}
            )
            jobs = jobs_resp.json().get("data", [])

        # Build context object for AI injection
        context = {
            "is_returning_customer": True,
            "customer_name": customer.get("name", ""),
            "membership": customer.get("membershipStatus"),
            "recent_jobs": [
                {
                    "type": j.get("summary", ""),
                    "status": j.get("jobStatus", ""),
                    "date": j.get("completedOn", ""),
                }
                for j in jobs[:3]
            ],
        }
        return context

    except Exception:
        return None  # Graceful fallback — never block the call


def build_context_prompt(context: dict | None) -> str:
    """
    Converts ST customer context into a prompt injection for the AI Receptionist.
    """
    if not context or not context.get("is_returning_customer"):
        return ""

    name = context.get("customer_name", "this customer")
    jobs = context.get("recent_jobs", [])
    membership = context.get("membership")

    lines = [f"This is a RETURNING CUSTOMER. Their name is {name}."]
    if membership:
        lines.append(f"They have an active {membership} membership.")
    if jobs:
        last = jobs[0]
        lines.append(f"Most recent job: {last['type']} ({last['status']}, {last['date'][:10] if last['date'] else 'date unknown'}).")

    lines.append(
        "Reference their history naturally — make them feel recognized, not processed. "
        "Example: 'Welcome back, [name]. I see we helped you with [last job] — what can we do for you today?'"
    )
    return "\n".join(lines)
