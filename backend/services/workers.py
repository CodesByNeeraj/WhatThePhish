"""Background thread workers and the response poll loop."""
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import backend.config  # noqa: F401 — ensures .env and sys.path are set

executor = ThreadPoolExecutor(max_workers=3)


def run_campaign_sync(campaign_id: str, req) -> None:
    """Runs CampaignFlow in a thread (blocking — must not run on the event loop)."""
    try:
        from agenticantiphish.campaign_flow import CampaignFlow, CampaignState

        flow = CampaignFlow()
        flow.state.campaign_id       = campaign_id
        flow.state.department        = req.department
        flow.state.urgency           = req.urgency
        flow.state.technique         = req.technique
        flow.state.recipient_list    = [r.model_dump() for r in req.recipients]
        flow.state.tracking_base_url = os.environ.get("TRACKING_BASE_URL", "http://localhost:8001")
        flow.kickoff()
    except Exception as e:
        import traceback
        print(f"\n[workers] CampaignFlow CRASHED for {campaign_id}:")
        traceback.print_exc()


def run_response_sync() -> None:
    """Runs ResponseFlow in a thread (blocking — must not run on the event loop)."""
    from agenticantiphish.response_flow import ResponseFlow

    ResponseFlow().kickoff()


async def response_poll_loop() -> None:
    """Polls for new phishing clicks every 30 seconds and triggers remediation."""
    while True:
        await asyncio.sleep(30)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, run_response_sync)
        print("[workers] Response poll complete.")
