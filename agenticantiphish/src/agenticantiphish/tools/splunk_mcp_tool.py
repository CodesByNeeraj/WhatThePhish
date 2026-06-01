import asyncio
import os
from typing import Type

import httpx
from crewai.tools import BaseTool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import BaseModel, Field


class SplunkMCPInput(BaseModel):
    query: str = Field(..., description="Splunk SPL query to execute.")
    earliest_time: str = Field(default="-1h", description="Earliest time bound (e.g. '-1h', '-24h').")
    latest_time: str = Field(default="now", description="Latest time bound.")


class SplunkMCPTool(BaseTool):
    name: str = "SplunkMCPTool"
    description: str = (
        "Run a Splunk SPL search query via the Splunk MCP server. "
        "Use this to detect phishing click events, retrieve campaign data, "
        "or check training completion. Returns the raw query result as text."
    )
    args_schema: Type[BaseModel] = SplunkMCPInput

    def _run(self, query: str, earliest_time: str = "-1h", latest_time: str = "now") -> str:
        try:
            return asyncio.run(self._async_query(query, earliest_time, latest_time))
        except RuntimeError:
            # Already inside an event loop (e.g. Jupyter) — use nest_asyncio or thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run, self._async_query(query, earliest_time, latest_time)
                )
                return future.result()

    async def _async_query(self, query: str, earliest_time: str, latest_time: str) -> str:
        endpoint = os.environ.get(
            "SPLUNK_MCP_ENDPOINT", "https://localhost:8089/services/mcp"
        )
        token = os.environ.get("SPLUNK_MCP_TOKEN", "")

        def make_client(**kwargs):
            return httpx.AsyncClient(verify=False, **kwargs)

        try:
            async with streamablehttp_client(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                httpx_client_factory=make_client,
            ) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "splunk_run_query",
                        arguments={
                            "query": query,
                            "earliest_time": earliest_time,
                            "latest_time": latest_time,
                        },
                    )
                    if result.content:
                        return result.content[0].text
                    return "[]"
        except Exception as e:
            return f"SplunkMCPTool error: {e}"
