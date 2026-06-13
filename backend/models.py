from pydantic import BaseModel


class Recipient(BaseModel):
    email: str
    name: str = ""


class CampaignRequest(BaseModel):
    department: str
    urgency: str    # low | medium | high
    technique: str  # credential_harvesting | invoice_fraud | it_helpdesk |
                    # executive_impersonation | delivery_notification
    recipients: list[Recipient]
