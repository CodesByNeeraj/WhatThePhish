from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str]                   = mapped_column(String, primary_key=True)
    department: Mapped[str]           = mapped_column(String)
    urgency: Mapped[str]              = mapped_column(String)
    technique: Mapped[str]            = mapped_column(String)
    email_subject: Mapped[str]        = mapped_column(String, default="")
    email_html_body: Mapped[str]      = mapped_column(Text, default="")
    sender_name: Mapped[str]          = mapped_column(String, default="")
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    recipients: Mapped[list["Recipient"]] = relationship(back_populates="campaign", lazy="select")
    clicks: Mapped[list["Click"]]         = relationship(back_populates="campaign", lazy="select")


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[str]  = mapped_column(String, ForeignKey("campaigns.id"))
    email: Mapped[str]        = mapped_column(String)
    name: Mapped[str]         = mapped_column(String, default="")
    token: Mapped[str]        = mapped_column(String, unique=True, index=True)
    tracking_url: Mapped[str] = mapped_column(String)

    campaign: Mapped["Campaign"] = relationship(back_populates="recipients")


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int]               = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str]            = mapped_column(String, index=True)
    employee_email: Mapped[str]   = mapped_column(String)
    department: Mapped[str]       = mapped_column(String)
    campaign_id: Mapped[str]      = mapped_column(String, ForeignKey("campaigns.id"))
    clicked_at: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    response_sent: Mapped[bool]   = mapped_column(Boolean, default=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="clicks")
