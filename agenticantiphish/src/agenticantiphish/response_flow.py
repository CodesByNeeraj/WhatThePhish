import json
import time

from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

from agenticantiphish.detection_crew import DetectionCrew
from agenticantiphish.response_crew import ResponseCrew


class ResponseState(BaseModel):
    clickers: list[dict] = []
    responses_sent: int = 0


def _get_unprocessed_clicks() -> list[dict]:
    """Detect unresponded clicks via Splunk MCP, enrich with campaign details from DB."""
    t0 = time.time()

    # Query Splunk via MCP — returns clicks with no training event yet
    try:
        result = DetectionCrew().crew().kickoff()
        raw = result.raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        splunk_clicks: list[dict] = json.loads(raw) if raw else []
        print(f"[ResponseFlow] MCP query took {time.time() - t0:.2f}s — {len(splunk_clicks)} unresponded clicks")
    except Exception as e:
        print(f"[ResponseFlow] MCP detection failed ({e})")
        return []

    if not splunk_clicks:
        return []

    # Enrich with campaign context from DB; skip already-responded clicks
    try:
        from backend.database import SessionLocal
        from backend.db_models import Campaign, Click

        enriched = []
        with SessionLocal() as db:
            for sc in splunk_clicks:
                token = sc.get("token", "")
                click = db.query(Click).filter(Click.token == token).first()
                if not click or click.response_sent:
                    continue  # already sent training — skip
                campaign = db.query(Campaign).filter(Campaign.id == click.campaign_id).first()
                if campaign:
                    enriched.append({
                        "token":            token,
                        "employee_email":   click.employee_email,
                        "department":       click.department,
                        "campaign_id":      click.campaign_id,
                        "technique":        campaign.technique,
                        "phishing_subject": campaign.email_subject,
                        "phishing_sender":  campaign.sender_name,
                    })
        return enriched
    except Exception as e:
        print(f"[ResponseFlow] DB enrichment failed: {e}")
        return []


def _mark_click_responded(token: str) -> None:
    try:
        from backend.database import SessionLocal
        from backend.db_models import Click

        with SessionLocal() as db:
            click = db.query(Click).filter(Click.token == token).first()
            if click:
                click.response_sent = True
                db.commit()
    except Exception as e:
        print(f"[ResponseFlow] Failed to mark click responded: {e}")


class ResponseFlow(Flow[ResponseState]):
    """
    Detects unprocessed phishing clicks from the DB and triggers
    automated remediation via ResponseCrew for each one.
    """

    @start()
    def detect_clicks(self) -> None:
        self.state.clickers = _get_unprocessed_clicks()
        print(f"[ResponseFlow] Unprocessed clicks: {len(self.state.clickers)}")

    @router(detect_clicks)
    def route_on_clickers(self) -> str:
        return "clicks_found" if self.state.clickers else "no_clicks"

    @listen("clicks_found")
    def respond_to_clickers(self) -> None:
        for clicker in self.state.clickers:
            token          = clicker["token"]
            employee_email = clicker["employee_email"]

            print(f"[ResponseFlow] Responding to {employee_email} (token={token})")
            ResponseCrew().crew().kickoff(
                inputs={
                    "employee_email":   employee_email,
                    "token":            token,
                    "campaign_id":      clicker["campaign_id"],
                    "department":       clicker["department"],
                    "technique":        clicker["technique"],
                    "phishing_subject": clicker["phishing_subject"],
                    "phishing_sender":  clicker["phishing_sender"],
                }
            )
            _mark_click_responded(token)
            self.state.responses_sent += 1

        print(f"[ResponseFlow] Done. Responses sent: {self.state.responses_sent}")

    @listen("no_clicks")
    def no_action_needed(self) -> None:
        print("[ResponseFlow] No new clicks.")
