import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from agenticantiphish.campaign_crew import CampaignCreationCrew
from agenticantiphish.dispatch_crew import EmailDispatchCrew


class CampaignState(BaseModel):
    # ── Inputs ────────────────────────────────────────────────────────────────
    campaign_id: str = ""
    department: str = ""
    urgency: str = ""
    technique: str = ""
    recipient_list: list[dict] = []   # [{email, name}]
    tracking_base_url: str = "http://localhost:8000"

    # ── After CampaignCreationCrew ─────────────────────────────────────────────
    recipients: list[dict] = []       # [{email, name, token, tracking_url}]
    email_subject: str = ""
    email_html_body: str = ""
    sender_name: str = ""

    # ── After EmailDispatchCrew ────────────────────────────────────────────────
    dispatch_summary: str = ""


def _make_token(email: str, campaign_id: str) -> str:
    seed = f"{email}:{campaign_id}:{uuid.uuid4()}"
    return hashlib.sha256(seed.encode()).hexdigest()[:16]


def _save_campaign(state: CampaignState) -> None:
    try:
        from backend.database import SessionLocal
        from backend.db_models import Campaign, Recipient

        with SessionLocal() as db:
            campaign = db.query(Campaign).filter(Campaign.id == state.campaign_id).first()
            if campaign:
                campaign.email_subject        = state.email_subject
                campaign.email_html_body      = state.email_html_body
                campaign.sender_name          = state.sender_name
            else:
                db.add(Campaign(
                    id=state.campaign_id,
                    department=state.department,
                    urgency=state.urgency,
                    technique=state.technique,
                    email_subject=state.email_subject,
                    email_html_body=state.email_html_body,
                    sender_name=state.sender_name,
                ))

            for r in state.recipients:
                if not db.query(Recipient).filter(Recipient.token == r["token"]).first():
                    db.add(Recipient(
                        campaign_id=state.campaign_id,
                        email=r["email"],
                        name=r.get("name", ""),
                        token=r["token"],
                        tracking_url=r["tracking_url"],
                    ))
            db.commit()
    except Exception as e:
        print(f"[campaign_flow] DB save failed: {e}")


def _log_sent_events(state: "CampaignState") -> None:
    from backend.services.splunk import log_sent
    for r in state.recipients:
        log_sent(
            token=r["token"],
            employee_email=r["email"],
            department=state.department,
            campaign_id=state.campaign_id,
        )


class CampaignFlow(Flow[CampaignState]):
    """
    Orchestrates phishing campaign creation and dispatch.

    Flow:
      generate_email_content  →  CampaignCreationCrew (planner + generator)
      dispatch_emails         →  EmailDispatchCrew    (dispatcher)
    """

    @start()
    def generate_email_content(self) -> None:
        # Generate unique tracking tokens for every recipient before calling crew
        base_url = self.state.tracking_base_url
        self.state.recipients = [
            {
                "email": r["email"],
                "name": r.get("name", r["email"].split("@")[0]),
                "token": _make_token(r["email"], self.state.campaign_id),
                "tracking_url": "",  # filled below after token creation
            }
            for r in self.state.recipient_list
        ]
        for r in self.state.recipients:
            r["tracking_url"] = f"{base_url}/track/{r['token']}"

        result = CampaignCreationCrew().crew().kickoff(
            inputs={
                "campaign_id": self.state.campaign_id,
                "department": self.state.department,
                "urgency": self.state.urgency,
                "technique": self.state.technique,
            }
        )

        # The final task (generate_phishing_email_task) outputs JSON
        raw = result.raw.strip()
        # Strip markdown code fences if the LLM wrapped output in ```json ... ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            email_data: dict[str, Any] = json.loads(raw)
            self.state.email_subject = email_data.get("subject", "")
            self.state.email_html_body = email_data.get("html_body", "")
            self.state.sender_name = email_data.get("sender_name") or "IT Support"
        except json.JSONDecodeError:
            # Fallback: store raw output as body — agent didn't return clean JSON
            self.state.email_html_body = result.raw
            self.state.email_subject = f"Important notice for {self.state.department}"
            self.state.sender_name = "IT Support"

    @listen(generate_email_content)
    def dispatch_emails(self) -> None:
        _save_campaign(self.state)

        result = EmailDispatchCrew().crew().kickoff(
            inputs={
                "campaign_id": self.state.campaign_id,
                "department": self.state.department,
                "email_subject": self.state.email_subject,
                "email_html_body": self.state.email_html_body,
                "sender_name": self.state.sender_name,
                "recipients_json": json.dumps(self.state.recipients),
            }
        )
        self.state.dispatch_summary = result.raw
        print(f"\n[CampaignFlow] Dispatch complete: {result.raw}")

        # Log phishing:sent events directly — don't rely on the agent for this
        _log_sent_events(self.state)
