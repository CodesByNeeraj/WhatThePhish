from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from backend.services import splunk
from backend.services.store import find_recipient_by_token, record_click

router = APIRouter(tags=["tracking"])

PHISHED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Security Awareness — Phishing Simulation</title>
  <style>
    body {
      margin: 0;
      padding: 40px 16px;
      font-family: Georgia, serif;
      background: #fff;
      color: #222;
    }
    .wrap {
      max-width: 520px;
      margin: 60px auto 0;
    }
    .label {
      font-family: Arial, sans-serif;
      font-size: 11px;
      font-weight: bold;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: #888;
      margin-bottom: 20px;
    }
    h1 {
      font-size: 28px;
      font-weight: normal;
      line-height: 1.3;
      margin: 0 0 20px 0;
      color: #111;
    }
    .divider {
      border: none;
      border-top: 1px solid #e0e0e0;
      margin: 24px 0;
    }
    p {
      font-size: 15px;
      line-height: 1.8;
      color: #444;
      margin: 0 0 16px 0;
    }
    .next {
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #e0e0e0;
    }
    .next-label {
      font-family: Arial, sans-serif;
      font-size: 11px;
      font-weight: bold;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      color: #888;
      margin-bottom: 10px;
    }
    .next p {
      font-size: 14px;
      color: #555;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="label">Security Simulation</div>
    <div style="font-size:48px;margin-bottom:16px;">🎣</div>
    <h1>You clicked a phishing link.</h1>
    <hr class="divider">
    <p>
      This was an authorised security awareness test run by your IT Security team.
      No real harm has occurred and your credentials were never at risk.
    </p>
    <p>
      Phishing emails are designed to look legitimate — this one was crafted
      specifically to test your awareness. You are not in trouble.
    </p>
    <div class="next">
      <div class="next-label">What happens next</div>
      <p>
        Check your inbox shortly. You will receive a personalised email explaining
        exactly what made this a phishing attempt and what to look out for next time.
      </p>
    </div>
  </div>
</body>
</html>"""

#called by employees browser when they click the phishing link in the email. The link contains a unique token that identifies the employee and campaign. This endpoint logs the click event to Splunk HEC and also records it locally for reporting purposes, then returns a landing page informing the employee about the simulation.
@router.get("/track/{token}", response_class=HTMLResponse)
async def track_click(token: str):
    """
    Called when an employee clicks the phishing link.
    Logs the event to Splunk HEC and locally, then returns the landing page.
    """
    recipient = find_recipient_by_token(token)
    if recipient:
        splunk.log_click(
            token=token,
            employee_email=recipient["email"],
            department=recipient["department"],
            campaign_id=recipient["campaign_id"],
        )
        record_click(
            token=token,
            employee_email=recipient["email"],
            department=recipient["department"],
            campaign_id=recipient["campaign_id"],
        )
    return HTMLResponse(content=PHISHED_HTML, status_code=200)
