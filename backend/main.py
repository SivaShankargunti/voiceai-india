"""
India SME Voice AI — FastAPI Backend
Handles: business registration, campaigns, analytics, compliance
"""

import sys
import os

# Add parent directory to path so we can import compliance
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from backend import database as db
from compliance.trai import TRAIComplianceEngine, CallType, CallOutcome

# Initialize database
db.init_db()

app = FastAPI(
    title="VoiceAI India API",
    description="India-first Voice AI platform for SMEs",
    version="0.1.0",
)

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== REQUEST MODELS =====

class BusinessRegister(BaseModel):
    name: str
    industry: str = "general"  # clinic, restaurant, realestate, ecommerce
    owner_name: str
    owner_phone: str
    owner_email: str = ""
    language: str = "hi"  # hi, en, te, ta

class ContactAdd(BaseModel):
    phone: str
    name: str = ""
    tags: list[str] = []

class CampaignCreate(BaseModel):
    name: str
    call_type: str = "service"  # service, promotional, transactional
    script_template: str = ""
    language: str = "hi"

class ComplianceCheckRequest(BaseModel):
    phone: str
    call_type: str = "service"
    language: str = "hi"
    has_consent: bool = False

class CallLogRequest(BaseModel):
    contact_phone: str
    duration_seconds: int = 0
    outcome: str = "completed"
    call_type: str = "service"
    direction: str = "inbound"
    transcript: str = ""
    campaign_id: str = ""


# ===== ROUTES: HEALTH =====

@app.get("/")
async def root():
    return {
        "name": "VoiceAI India API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ===== ROUTES: BUSINESS =====

@app.post("/api/business/register")
async def register_business(biz: BusinessRegister):
    """Register a new SME business. Self-serve onboarding."""
    result = db.create_business(
        name=biz.name,
        industry=biz.industry,
        owner_name=biz.owner_name,
        owner_phone=biz.owner_phone,
        owner_email=biz.owner_email,
        language=biz.language,
    )
    return {"success": True, "business": result}

@app.get("/api/business/{business_id}")
async def get_business(business_id: str):
    """Get business details."""
    biz = db.get_business(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    return biz

@app.get("/api/businesses")
async def list_businesses():
    """List all registered businesses."""
    return db.list_businesses()


# ===== ROUTES: CONTACTS =====

@app.post("/api/business/{business_id}/contacts")
async def add_contact(business_id: str, contact: ContactAdd):
    """Add a contact to a business."""
    biz = db.get_business(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    result = db.add_contact(
        business_id=business_id,
        phone=contact.phone,
        name=contact.name,
        tags=contact.tags,
    )
    return {"success": True, "contact": result}

@app.get("/api/business/{business_id}/contacts")
async def get_contacts(business_id: str):
    """Get all contacts for a business."""
    return db.get_contacts(business_id)


# ===== ROUTES: CAMPAIGNS =====

@app.post("/api/business/{business_id}/campaigns")
async def create_campaign(business_id: str, campaign: CampaignCreate):
    """Create a new outbound calling campaign."""
    biz = db.get_business(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    result = db.create_campaign(
        business_id=business_id,
        name=campaign.name,
        call_type=campaign.call_type,
        script_template=campaign.script_template,
        language=campaign.language,
    )
    return {"success": True, "campaign": result}

@app.get("/api/business/{business_id}/campaigns")
async def get_campaigns(business_id: str):
    """Get all campaigns for a business."""
    return db.get_campaigns(business_id)


# ===== ROUTES: COMPLIANCE =====

@app.post("/api/compliance/check")
async def compliance_check(req: ComplianceCheckRequest):
    """
    Pre-call TRAI compliance check.
    Run this BEFORE making any outbound call.
    """
    engine = TRAIComplianceEngine(
        business_name="VoiceAI India",
        business_id="system",
    )

    call_type_map = {
        "service": CallType.SERVICE,
        "promotional": CallType.PROMOTIONAL,
        "transactional": CallType.TRANSACTIONAL,
    }
    call_type = call_type_map.get(req.call_type, CallType.SERVICE)

    result = engine.validate_call(
        phone=req.phone,
        call_type=call_type,
        language=req.language,
        has_consent=req.has_consent,
    )

    return {
        "can_call": result.can_call,
        "reasons": result.reasons,
        "within_hours": result.within_hours,
        "dnd_clear": result.dnd_clear,
        "number_series": result.number_series,
        "disclosure_hi": result.disclosure_text_hi,
        "disclosure_en": result.disclosure_text_en,
    }

@app.get("/api/compliance/calling-hours")
async def calling_hours():
    """Check if current time is within TRAI calling hours."""
    engine = TRAIComplianceEngine(business_name="system")
    return {
        "within_hours": engine.is_within_calling_hours(),
        "window": "10:00 AM - 7:00 PM IST",
        "safe_window": "10:30 AM - 6:30 PM IST",
        "status": engine.time_until_next_window(),
    }

@app.post("/api/compliance/opt-out/{phone}")
async def process_opt_out(phone: str):
    """Process an opt-out request from a caller."""
    engine = TRAIComplianceEngine(business_name="system")
    result = engine.process_opt_out(phone)
    return result


# ===== ROUTES: CALL LOGS =====

@app.post("/api/business/{business_id}/calls/log")
async def log_call(business_id: str, call: CallLogRequest):
    """Log a call (TRAI audit requirement)."""
    result = db.log_call(
        business_id=business_id,
        contact_phone=call.contact_phone,
        duration_seconds=call.duration_seconds,
        outcome=call.outcome,
        call_type=call.call_type,
        direction=call.direction,
        transcript=call.transcript,
        campaign_id=call.campaign_id,
    )
    return {"success": True, "call_log": result}


# ===== ROUTES: ANALYTICS =====

@app.get("/api/business/{business_id}/analytics")
async def get_analytics(business_id: str):
    """Get call analytics for a business dashboard."""
    biz = db.get_business(business_id)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    analytics = db.get_analytics(business_id)
    analytics["business_name"] = biz["name"]
    analytics["plan"] = biz["plan"]
    analytics["minutes_limit"] = biz["monthly_minutes_limit"]
    return analytics


# ===== RUN =====

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting VoiceAI India Backend...")
    print("📄 API Docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)