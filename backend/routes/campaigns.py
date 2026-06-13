import asyncio
import uuid

from fastapi import APIRouter, HTTPException

from backend.database import SessionLocal
from backend.db_models import Campaign, Click, Recipient
from backend.models import CampaignRequest
from backend.services import store, workers

router = APIRouter(prefix="/api", tags=["campaigns"])


@router.post("/campaign", status_code=202)
async def create_campaign(req: CampaignRequest):
    """
    Create a campaign record immediately, then run the agent flow in the background.
    The campaign appears in the list right away; agents enrich it with email content.
    """
    campaign_id = f"camp_{uuid.uuid4().hex[:8]}"

    with SessionLocal() as db:
        db.add(Campaign(
            id=campaign_id,
            department=req.department,
            urgency=req.urgency,
            technique=req.technique,
        ))
        db.commit()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        workers.executor,
        lambda: workers.run_campaign_sync(campaign_id, req),
    )

    return {
        "campaign_id": campaign_id,
        "status": "launching",
        "message": "Campaign is being generated and dispatched in the background.",
    }


@router.get("/campaigns")
async def list_campaigns():
    return {"campaigns": store.list_campaigns()}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaign = store.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.delete("/campaigns", status_code=200)
async def reset_all_campaigns():
    """Delete all campaigns, recipients, and clicks — demo reset."""
    with SessionLocal() as db:
        db.query(Click).delete()
        db.query(Recipient).delete()
        db.query(Campaign).delete()
        db.commit()
    return {"message": "All campaigns cleared."}
