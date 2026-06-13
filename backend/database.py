import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import backend.config  # noqa: F401 — ensures .env is loaded before reading DATABASE_URL

_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./whatthephish.db")

# Render (and older Heroku) emit postgres:// — SQLAlchemy requires postgresql://
if _DATABASE_URL.startswith("postgres://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://", 1)

_connect_args = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(_DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from backend.db_models import Campaign, Recipient, Click  # noqa: F401
    Base.metadata.create_all(bind=engine)
