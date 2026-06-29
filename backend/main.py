"""
WebStaffr — FastAPI Application
Run: uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .db.models import init_db
from .routes.webhooks import router as webhook_router
from .routes.dashboard import router as dashboard_router

app = FastAPI(
    title="WebStaffr",
    description="AI Office Staff for Home Service Contractors — webstaffr.com",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ WebStaffr running. DB initialized.")

app.include_router(webhook_router)
app.include_router(dashboard_router)

# Serve operator dashboard as static site
frontend_dir = Path(__file__).parent.parent / "frontend" / "dashboard"
if frontend_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=str(frontend_dir), html=True), name="dashboard")

@app.get("/health")
def health():
    return {"status": "ok", "service": "WebStaffr"}

@app.get("/")
def root():
    return {
        "service": "WebStaffr API",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "webhooks": {
            "missed_call": "POST /webhooks/voice/incoming",
            "lead_form": "POST /webhooks/lead-form",
            "job_complete": "POST /webhooks/job-complete",
        },
        "integrations": {
            "servicetitan_phase1": "Zapier bridge — active",
            "servicetitan_phase2": "Native OAuth — weeks 4-8",
            "jobber": "Zapier bridge — same pattern",
        }
    }
