"""
Queries Splunk for employees in a given department via MCP.
Direct MCP call — no agent overhead needed for a simple lookup.
"""
import asyncio
import json
import os

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

import backend.config  # noqa: F401


async def _query_async(department: str) -> list[dict]:
    endpoint = os.environ.get("SPLUNK_MCP_ENDPOINT", "https://localhost:8089/services/mcp")
    token    = os.environ.get("SPLUNK_MCP_TOKEN", "")
    index    = os.environ.get("SPLUNK_EMPLOYEES_INDEX", "employees")

    query = f'search index={index} department="{department}" | table email, name, department | dedup email'

    def make_client(**kwargs):
        return httpx.AsyncClient(verify=False, **kwargs)

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
                    "query":         query,
                    "earliest_time": "-30d",
                    "latest_time":   "now",
                },
            )
            raw = result.content[0].text if result.content else "[]"
            return _parse(raw)


def _parse(raw: str) -> list[dict]:
    """Parse Splunk query results into a clean list of employee dicts."""
    try:
        data = json.loads(raw)
        # Handle {"results": [...]} or plain [...]
        rows = data.get("results", data) if isinstance(data, dict) else data
        employees = []
        for row in rows:
            email = row.get("email", "").strip()
            name  = row.get("name", "").strip()
            if email:
                employees.append({"email": email, "name": name})
        return employees
    except Exception:
        return []


def get_employees_by_department(department: str) -> list[dict]:
    """Synchronous wrapper — safe to call from FastAPI route handlers."""
    try:
        return asyncio.run(_query_async(department))
    except RuntimeError:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, _query_async(department)).result()
