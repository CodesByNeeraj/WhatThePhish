import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EmailSendInput(BaseModel):
    to_email: str = Field(..., description="Recipient email address.")
    subject: str = Field(..., description="Email subject line.")
    html_body: str = Field(..., description="Full HTML body of the email.")
    sender_name: str = Field(default="IT Security Team", description="Display name of the sender.")
    sender_email: str = Field(default="", description="Sender display address (optional).")


class EmailSendTool(BaseTool):
    name: str = "EmailSendTool"
    description: str = (
        "Send an HTML email via Gmail SMTP. Use for phishing simulation emails "
        "and remediation/training emails."
    )
    args_schema: Type[BaseModel] = EmailSendInput

    def _run(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        sender_name: str = "IT Security Team",
        sender_email: str = "",
    ) -> str:
        smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_pass = os.environ.get("SMTP_PASS", "")

        display_from = f"{sender_name} <{sender_email or smtp_user}>"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = display_from
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, to_email, msg.as_string())
            return f"Email sent to {to_email} — subject: '{subject}'"
        except smtplib.SMTPAuthenticationError:
            return "SMTP auth failed. Check SMTP_USER and SMTP_PASS in .env."
        except Exception as e:
            return f"Email send failed for {to_email}: {e}"
