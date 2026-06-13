import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Must run at import time — sets env vars before any CrewAI import touches them
_env_path = Path(__file__).parent.parent / "agenticantiphish" / ".env"
load_dotenv(dotenv_path=_env_path)

# Make the agenticantiphish package importable from anywhere
_pkg_path = str(Path(__file__).parent.parent / "agenticantiphish" / "src")
if _pkg_path not in sys.path:
    sys.path.insert(0, _pkg_path)

# Absolute path to campaigns directory — used by store.py and workers.py
CAMPAIGNS_DIR = Path(__file__).parent.parent / "agenticantiphish" / "campaigns"
CAMPAIGNS_DIR.mkdir(exist_ok=True)
