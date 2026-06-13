"""Direct Splunk HEC client for the tracking endpoint.
Intentionally separate from the CrewAI SplunkHECTool — this path must be
fast (sub-second) and has no agent overhead.
"""
import os

import httpx

import backend.config  # noqa: F401 — ensures .env is loaded

# Logs a click event to Splunk HEC with relevant metadata about the employee and campaign. triggered by employee clicking the phishing link in the email. The link contains a unique token that identifies the employee and campaign, which is used to enrich the log event for later analysis and reporting.
def log_click(
    token: str,
    employee_email: str,
    department: str,
    campaign_id: str,
) -> None:
    hec_url = os.environ.get("SPLUNK_HEC_URL", "https://localhost:8088/services/collector")
    hec_token = os.environ.get("SPLUNK_HEC_TOKEN", "")
    index = os.environ.get("SPLUNK_INDEX", "phishing_sim")

    try:
        httpx.post(
            hec_url,
            headers={"Authorization": f"Splunk {hec_token}"},
            json={
                "event": {
                    "type": "phishing_click",
                    "token": token,
                    "employee_email": employee_email,
                    "department": department,
                    "campaign_id": campaign_id,
                    "is_simulation": True,
                },
                "index": index,
                "sourcetype": "phishing:click",
            },
            verify=False,
            timeout=5,
        )
    except Exception as e:
        print(f"[splunk] HEC error on click log: {e}")

# Logs a sent event to Splunk HEC with relevant metadata about the employee and campaign. triggered when a phishing email is sent to an employee. The log includes a unique token that identifies the employee and campaign, allowing for later analysis of email delivery and engagement metrics in Splunk.
# This function is called in camplaign_flow.py after emails are sent out by the agent
def log_sent(
    token: str,
    employee_email: str,
    department: str,
    campaign_id: str,
) -> None:
    hec_url = os.environ.get("SPLUNK_HEC_URL", "https://localhost:8088/services/collector")
    hec_token = os.environ.get("SPLUNK_HEC_TOKEN", "")
    index = os.environ.get("SPLUNK_INDEX", "phishing_sim")

    try:
        httpx.post(
            hec_url,
            headers={"Authorization": f"Splunk {hec_token}"},
            json={
                "event": {
                    "type": "phishing_sent",
                    "token": token,
                    "employee_email": employee_email,
                    "department": department,
                    "campaign_id": campaign_id,
                    "is_simulation": True,
                },
                "index": index,
                "sourcetype": "phishing:sent",
            },
            verify=False,
            timeout=5,
        )
    except Exception as e:
        print(f"[splunk] HEC error on sent log: {e}")
