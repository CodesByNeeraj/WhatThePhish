"""
One-time script to load mock employee data into Splunk.
Run once from the project root: python backend/scripts/seed_employees.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / "agenticantiphish" / ".env")

import httpx

HEC_URL   = os.environ.get("SPLUNK_HEC_URL", "https://localhost:8088/services/collector")
HEC_TOKEN = os.environ.get("SPLUNK_HEC_TOKEN", "")
INDEX     = os.environ.get("SPLUNK_EMPLOYEES_INDEX", "employees")

EMPLOYEES = [
    {"email": "alice.chen@company.com",   "name": "Alice Chen",    "department": "Finance"},
    {"email": "bob.smith@company.com",    "name": "Bob Smith",     "department": "Finance"},
    {"email": "carol.jones@company.com",  "name": "Carol Jones",   "department": "HR"},
    {"email": "david.brown@company.com",  "name": "David Brown",   "department": "HR"},
    {"email": "eve.wilson@company.com",   "name": "Eve Wilson",    "department": "Engineering"},
    {"email": "frank.davis@company.com",  "name": "Frank Davis",   "department": "Engineering"},
    {"email": "grace.miller@company.com", "name": "Grace Miller",  "department": "Sales"},
    {"email": "henry.taylor@company.com", "name": "Henry Taylor",  "department": "Sales"},
    {"email": "iris.white@company.com",   "name": "Iris White",    "department": "Operations"},
    {"email": "jack.martin@company.com",  "name": "Jack Martin",   "department": "Operations"},
    {"email": "karen.lee@company.com",    "name": "Karen Lee",     "department": "Executive"},
    {"email": "liam.nguyen@company.com",  "name": "Liam Nguyen",   "department": "Executive"},
    {"email": "mia.clark@company.com",    "name": "Mia Clark",     "department": "Marketing"},
    {"email": "noah.hall@company.com",    "name": "Noah Hall",     "department": "Marketing"},
    {"email": "olivia.adams@company.com", "name": "Olivia Adams",  "department": "Legal"},
    {"email": "peter.scott@company.com",  "name": "Peter Scott",   "department": "Legal"},
]


def seed():
    if not HEC_TOKEN:
        print("ERROR: SPLUNK_HEC_TOKEN not set in .env")
        sys.exit(1)

    success = 0
    for emp in EMPLOYEES:
        try:
            res = httpx.post(
                HEC_URL,
                headers={"Authorization": f"Splunk {HEC_TOKEN}"},
                json={
                    "event":      emp,
                    "index":      INDEX,
                    "sourcetype": "employee:directory",
                },
                verify=False,
                timeout=5,
            )
            res.raise_for_status()
            print(f"  ok  {emp['name']} ({emp['department']})")
            success += 1
        except Exception as e:
            print(f"  FAIL  {emp['name']} — {e}")

    print(f"\nDone. {success}/{len(EMPLOYEES)} employees seeded into index={INDEX}")


if __name__ == "__main__":
    seed()
