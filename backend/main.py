import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import backend.config  # noqa: F401 — must be first: loads .env and sets sys.path
from backend.database import init_db
from backend.routes import campaigns, employees, stats, tracking
from backend.services.workers import response_poll_loop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

_FRONTEND = Path(__file__).parent.parent / "frontend" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    poll_task = asyncio.create_task(response_poll_loop())
    print("[WhatThePhish] DB initialised. Response polling started (every 30s).")
    yield
    poll_task.cancel()


app = FastAPI(title="WhatThePhish API", version="1.0.0", lifespan=lifespan)

_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracking.router)
app.include_router(campaigns.router)
app.include_router(stats.router)
app.include_router(employees.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    return HTMLResponse(content=_FRONTEND.read_text(encoding="utf-8"))


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "WhatThePhish API"}
