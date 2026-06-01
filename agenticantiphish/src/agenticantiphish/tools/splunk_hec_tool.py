import json
import os
from typing import Type

import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SplunkHECInput(BaseModel):
    event: dict = Field(..., description="The event payload to log to Splunk.")
    sourcetype: str = Field(
        default="phishing:event",
        description="Splunk sourcetype (e.g. 'phishing:sent', 'phishing:click', 'phishing:training').",
    )


class SplunkHECTool(BaseTool):
    name: str = "SplunkHECTool"
    description: str = (
        "Log an event to Splunk via HTTP Event Collector (HEC). "
        "Use this to record campaign sends, click events, and training enrolments. "
        "Provide the event as a dict and a sourcetype string."
    )
    args_schema: Type[BaseModel] = SplunkHECInput

    def _run(self, event: dict, sourcetype: str = "phishing:event") -> str:
        hec_url = os.environ.get(
            "SPLUNK_HEC_URL", "https://localhost:8088/services/collector"
        )
        token = os.environ.get("SPLUNK_HEC_TOKEN", "")
        index = os.environ.get("SPLUNK_INDEX", "phishing_sim")

        payload = {"event": event, "index": index, "sourcetype": sourcetype}

        try:
            response = httpx.post(
                hec_url,
                headers={"Authorization": f"Splunk {token}"},
                json=payload,
                verify=False,
                timeout=10,
            )
            response.raise_for_status()
            return f"Splunk HEC: event logged. sourcetype={sourcetype} event={json.dumps(event)}"
        except httpx.HTTPStatusError as e:
            return f"Splunk HEC HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return f"Splunk HEC error: {e}"
