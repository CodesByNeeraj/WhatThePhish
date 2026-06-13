"""Database operations — replaces the old JSON file store."""
from backend.database import SessionLocal
from backend.db_models import Campaign, Click, Recipient


def find_recipient_by_token(token: str) -> dict | None:
    with SessionLocal() as db:
        r = db.query(Recipient).filter(Recipient.token == token).first()
        if not r:
            return None
        return {
            "email": r.email,
            "name": r.name,
            "token": r.token,
            "tracking_url": r.tracking_url,
            "campaign_id": r.campaign_id,
            "department": r.campaign.department,
        }


def list_campaigns() -> list[dict]:
    with SessionLocal() as db:
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return [
            {
                "campaign_id": c.id,
                "department": c.department,
                "technique": c.technique,
                "urgency": c.urgency,
                "recipients_count": len(c.recipients),
            }
            for c in campaigns
        ]


def get_campaign(campaign_id: str) -> dict | None:
    with SessionLocal() as db:
        c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not c:
            return None
        return {
            "campaign_id": c.id,
            "department": c.department,
            "urgency": c.urgency,
            "technique": c.technique,
            "email_subject": c.email_subject,
            "sender_name": c.sender_name,
            "recipients": [
                {"email": r.email, "name": r.name, "token": r.token}
                for r in c.recipients
            ],
        }


def record_click(token: str, employee_email: str, department: str, campaign_id: str) -> None:
    with SessionLocal() as db:
        already_exists = db.query(Click).filter(Click.token == token).first()
        if not already_exists:
            db.add(Click(
                token=token,
                employee_email=employee_email,
                department=department,
                campaign_id=campaign_id,
            ))
            db.commit()


def get_stats() -> dict:
    with SessionLocal() as db:
        total_campaigns    = db.query(Campaign).count()
        total_sent         = db.query(Recipient).count()
        total_clicks       = db.query(Click).count()
        total_remediations = db.query(Click).filter(Click.response_sent == True).count()  # noqa: E712

        by_department: dict[str, dict] = {}
        for c in db.query(Campaign).all():
            dept = c.department
            if dept not in by_department:
                by_department[dept] = {"sent": 0, "clicks": 0}
            by_department[dept]["sent"] += len(c.recipients)
            by_department[dept]["clicks"] += len(c.clicks)

        click_rate = round(total_clicks / total_sent * 100, 1) if total_sent > 0 else 0.0

        clickers = []
        for click in db.query(Click).order_by(Click.clicked_at.desc()).all():
            recipient = db.query(Recipient).filter(Recipient.token == click.token).first()
            clickers.append({
                "name":             recipient.name if recipient else "",
                "email":            click.employee_email,
                "department":       click.department,
                "campaign_id":      click.campaign_id,
                "clicked_at":       click.clicked_at.isoformat() + "Z",
                "training_sent":    click.response_sent,
            })

        return {
            "total_campaigns": total_campaigns,
            "total_emails_sent": total_sent,
            "total_clicks": total_clicks,
            "click_rate_percent": click_rate,
            "total_remediations_sent": total_remediations,
            "by_department": by_department,
            "clickers": clickers,
        }
