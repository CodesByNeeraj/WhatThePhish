# WhatThePhish

> Fully autonomous phishing simulation and security awareness platform powered by Agentic AI and Splunk.

![Architecture Diagram](./WhatThePhish%20Architecture%20Diagram.svg)

---

## What It Does

WhatThePhish runs end-to-end phishing simulations with zero manual intervention:

1. You create a campaign — choose a department, urgency level, and phishing technique.
2. A **Campaign Planner** agent analyses the parameters and produces a creative brief.
3. A **Phishing Email Generator** agent writes a convincing HTML phishing email from that brief.
4. An **Email Dispatcher** agent sends the email to each recipient with their unique tracking link.
5. When an employee clicks, the event is logged to Splunk in real time via HEC.
6. A **Splunk Monitor** agent queries Splunk MCP every 30 seconds to detect new clicks.
7. A **Threat Explainer** agent writes a personalised breakdown of the red flags in that specific email.
8. A **Training Content Generator** agent creates a tailored training module and quiz.
9. A **Response Sender** agent composes and sends the remediation email — all within 60 seconds of the click.

---

## Architecture

```
React Dashboard (5173)
        │
        ▼
FastAPI Backend (8001)
  ├── POST /api/campaign     → triggers CampaignFlow (background thread)
  ├── GET  /api/campaigns    → list campaigns from SQLite
  ├── GET  /api/stats        → dashboard metrics from SQLite
  ├── GET  /track/{token}    → logs click to Splunk HEC + SQLite
  └── GET  /api/employees/{dept} → queries Splunk MCP for employee list

CampaignFlow (CrewAI)
  ├── CampaignCreationCrew → AI generates phishing email (GPT-4o-mini)
  └── EmailDispatchCrew   → sends email per recipient via Gmail SMTP
                          → logs phishing:sent to Splunk HEC

ResponseFlow (every 30s)
  ├── DetectionCrew → queries Splunk MCP for phishing:click events
  └── ResponseCrew  → AI generates explanation + training → sends email
                    → logs phishing:training to Splunk HEC

Splunk
  ├── HEC (8088)  — receives phishing:sent, phishing:click, phishing:training
  └── MCP (8089)  — queried by agents for click detection + employee lookup
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI / Agents | OpenAI GPT-4o-mini via CrewAI 1.14.5a2 |
| Backend | FastAPI + Uvicorn |
| Database | SQLite (SQLAlchemy) |
| Splunk Ingestion | HTTP Event Collector (HEC) — direct HTTPS POST |
| Splunk Querying | Splunk MCP server |
| Email | Gmail SMTP (smtplib) |
| Frontend | React + Vite + Tailwind CSS |
| Package Manager | uv (recommended) or pip |
| Language | Python 3.10–3.13 |

---

## Prerequisites

- Python 3.10–3.13
- Node.js 18+
- Splunk Enterprise (local install) — free trial works
- A Gmail account with an App Password
- An OpenAI API key

---

## Splunk Setup

This is the most important part. Do this before anything else.

### 1. Install Splunk Enterprise

Download from [splunk.com](https://www.splunk.com/en_us/download/splunk-enterprise.html) and install locally. Default ports:
- Web UI: `localhost:8000`
- REST API / MCP: `localhost:8089`
- HEC: `localhost:8088`

### 2. Create the phishing_sim index

In Splunk web UI (`localhost:8000`):

```
Settings → Indexes → New Index
  Name: phishing_sim
  (leave all other settings as default)
```

### 3. Create the employees index

```
Settings → Indexes → New Index
  Name: employees
```

### 4. Enable HTTP Event Collector (HEC)

```
Settings → Data Inputs → HTTP Event Collector → Global Settings
  → Enable SSL: Yes (or No for local dev)
  → Default Index: phishing_sim
  → Save

Settings → Data Inputs → HTTP Event Collector → New Token
  → Name: WhatThePhish
  → Source type: Automatic
  → Index: phishing_sim
  → Review → Submit
  → Copy the token value → paste into .env as SPLUNK_HEC_TOKEN
```

### 5. Get your MCP token

```
Settings → Tokens (or Users → your user → Edit)
  → Generate a token for API access
  → Copy → paste into .env as SPLUNK_MCP_TOKEN
```

### 6. Verify HEC is working

**Windows (PowerShell):**
```powershell
curl -k -H "Authorization: Splunk YOUR_HEC_TOKEN" `
  -d '{"event":"test","index":"phishing_sim"}' `
  https://localhost:8088/services/collector
```

**Mac / Linux:**
```bash
curl -k -H "Authorization: Splunk YOUR_HEC_TOKEN" \
  -d '{"event":"test","index":"phishing_sim"}' \
  https://localhost:8088/services/collector
```

Expected response: `{"text":"Success","code":0}`

---

## Gmail App Password Setup

WhatThePhish sends emails via Gmail SMTP. You need an App Password (not your regular Gmail password).

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → must be enabled
3. Security → App passwords → Generate
4. Select app: Mail, device: Windows Computer → Generate
5. Copy the 16-character password → paste into `.env` as `SMTP_PASS`

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/CodesByNeeraj/WhatThePhish.git
cd WhatThePhish
```

### 2. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
pip install -e agenticantiphish
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Configure environment variables

**Windows (PowerShell):**
```powershell
copy agenticantiphish\.env.example agenticantiphish\.env
```

**Mac / Linux:**
```bash
cp agenticantiphish/.env.example agenticantiphish/.env
```

Open `agenticantiphish/.env` and fill in:

```env
OPENAI_API_KEY=sk-...              # Your OpenAI API key

SPLUNK_HEC_URL=https://localhost:8088/services/collector
SPLUNK_HEC_TOKEN=...               # From Splunk HEC setup above
SPLUNK_MCP_ENDPOINT=https://localhost:8089/services/mcp
SPLUNK_MCP_TOKEN=...               # From Splunk token setup above
SPLUNK_INDEX=phishing_sim
SPLUNK_EMPLOYEES_INDEX=employees

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com     # Your Gmail address
SMTP_PASS=xxxx xxxx xxxx xxxx      # Your Gmail App Password

TRACKING_BASE_URL=http://localhost:8001
DATABASE_URL=sqlite:///./whatthephish.db
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8001
```

### 6. Seed employee data into Splunk

Open `backend/scripts/seed_employees.py` and replace the `EMPLOYEES` list with your own employees or use the mock data provided:

```python
EMPLOYEES = [
    {"email": "john.smith@yourcompany.com", "name": "John Smith",  "department": "Finance"},
    {"email": "jane.doe@yourcompany.com",   "name": "Jane Doe",    "department": "Finance"},
    # Add more employees here
]
```

Then run:

```bash
python backend/scripts/seed_employees.py
```

Verify in Splunk: `index=employees | table email, name, department`

---

## Running the App

You need two terminals running simultaneously.

**Terminal 1 — Backend:**

Windows:
```powershell
.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8001
```

Mac / Linux:
```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8001
```

You should see: `[WhatThePhish] DB initialised. Response polling started (every 30s).`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`

---

## Running a Demo

1. Open `http://localhost:5173`
2. Click **New Campaign**
3. Select department, urgency, technique
4. Click **Import from Splunk** to auto-populate recipients, or type them manually (`email, Name` one per line)
5. Click **Launch Campaign**
6. Watch Terminal 1 — you'll see the AI agents running (takes 30–60s)
7. Check the target inbox — phishing email arrives
8. Click the tracking link in the email — you'll see the landing page
9. Watch Terminal 1 — within 30s the ResponseFlow detects the click via Splunk MCP
10. Check the inbox again — personalised explanation + training email arrives
11. Check Splunk: `index=phishing_sim | table _time, type, employee_email, department`
12. Dashboard updates automatically with click rates and training status

---

## Customisation

### Adding departments

In `frontend/src/components/NewCampaignModal.jsx`, line 4:

```javascript
const DEPARTMENTS = ['Finance', 'HR', 'Engineering', 'Sales', 'Operations',
                     'Executive', 'Marketing', 'Legal', 'IT', 'Security',
                     'YourNewDepartment'];  // ← add here
```

Then seed employees for that department in `backend/scripts/seed_employees.py` and re-run the seed script.

### Adding phishing techniques

In `frontend/src/components/NewCampaignModal.jsx`:

```javascript
const TECHNIQUES = [
  { value: 'credential_harvesting',   label: 'Credential Harvesting' },
  { value: 'invoice_fraud',           label: 'Invoice Fraud' },
  { value: 'it_helpdesk',             label: 'IT Helpdesk Impersonation' },
  { value: 'executive_impersonation', label: 'Executive Impersonation' },
  { value: 'delivery_notification',   label: 'Delivery Notification' },
  { value: 'your_new_technique',      label: 'Your New Technique' },  // ← add here
];
```

The AI agents automatically adapt to any technique value — no other changes needed.

### Changing urgency levels

Urgency levels (`high`, `medium`, `low`) are passed directly to the AI. Add new levels by editing the select options in `NewCampaignModal.jsx`.

### Changing email sign-offs per technique

In `agenticantiphish/src/agenticantiphish/config/campaign_tasks.yaml`:

```yaml
    - Close the email with a sign-off appropriate to the technique:
        credential_harvesting / it_helpdesk  → "IT Security Team"
        executive_impersonation              → "Office of the CEO"
        invoice_fraud                        → "Finance & Accounts"
        delivery_notification                → "Delivery Operations"
        your_new_technique                   → "Your Sign-off Here"  # ← add here
```

### Changing the response poll interval

In `backend/services/workers.py`:

```python
await asyncio.sleep(30)  # ← change to any number of seconds
```

---

## Resetting for a Fresh Demo

Clear all campaigns and clicks:

```bash
curl -X DELETE http://localhost:8001/api/campaigns
```

Or delete the DB file entirely (stop the backend first):

**Windows:**
```powershell
Remove-Item whatthephish.db
```

**Mac / Linux:**
```bash
rm whatthephish.db
```

Then restart uvicorn — it recreates the DB automatically.

Clear Splunk events:

```
index=phishing_sim | delete
```

(Requires `can_delete` role: Settings → Users → Edit → assign `can_delete`)

---

## Project Structure

```
WhatThePhish/
├── agenticantiphish/                  # CrewAI multi-agent package
│   ├── src/agenticantiphish/
│   │   ├── campaign_flow.py           # Phase 1+2: create + dispatch
│   │   ├── response_flow.py           # Phase 3+4: detect + respond
│   │   ├── campaign_crew.py           # AI email generation crew
│   │   ├── dispatch_crew.py           # Email sending crew
│   │   ├── detection_crew.py          # Splunk click detection crew
│   │   ├── response_crew.py           # Remediation email crew
│   │   ├── config/
│   │   │   ├── campaign_agents.yaml
│   │   │   ├── campaign_tasks.yaml
│   │   │   ├── dispatch_agents.yaml
│   │   │   ├── dispatch_tasks.yaml
│   │   │   ├── detection_agents.yaml
│   │   │   ├── detection_tasks.yaml
│   │   │   ├── response_agents.yaml
│   │   │   └── response_tasks.yaml
│   │   └── tools/
│   │       ├── email_tool.py          # Gmail SMTP tool for agents
│   │       ├── splunk_hec_tool.py     # HEC write tool for agents
│   │       └── splunk_mcp_tool.py     # MCP query tool for agents
│   └── .env                           # Environment variables (never commit)
├── backend/
│   ├── main.py                        # FastAPI app entrypoint
│   ├── db_models.py                   # SQLAlchemy DB models
│   ├── models.py                      # Pydantic request models
│   ├── database.py                    # SQLite engine setup
│   ├── config.py                      # Loads .env, sets sys.path
│   ├── routes/
│   │   ├── campaigns.py               # Campaign CRUD + reset
│   │   ├── tracking.py                # Click tracking endpoint
│   │   ├── stats.py                   # Dashboard stats
│   │   └── employees.py               # Splunk employee lookup
│   └── services/
│       ├── splunk.py                  # Direct HEC logging (log_click, log_sent)
│       ├── store.py                   # DB query functions
│       ├── workers.py                 # Background threads + poll loop
│       └── employee_lookup.py         # Splunk MCP employee query
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api/client.js
│       ├── hooks/useDashboard.js
│       └── components/
│           ├── Navbar.jsx
│           ├── StatCard.jsx
│           ├── DeptChart.jsx
│           ├── DeptTable.jsx
│           ├── CampaignsTable.jsx
│           ├── ClickersTable.jsx
│           └── NewCampaignModal.jsx
├── backend/scripts/
│   └── seed_employees.py              # One-time Splunk employees seeder
├── requirements.txt
├── ARCHITECTURE.md                    # Detailed architecture description
└── WhatThePhish Architecture Diagram.svg
```

---

## Splunk Event Schema

All events land in `index=phishing_sim`.

**phishing:sent** — logged when email is dispatched
```json
{"type": "phishing_sent", "employee_email": "...", "department": "...",
 "campaign_id": "...", "token": "...", "is_simulation": true}
```

**phishing:click** — logged when employee clicks the link
```json
{"type": "phishing_click", "employee_email": "...", "department": "...",
 "campaign_id": "...", "token": "...", "is_simulation": true}
```

**phishing:training** — logged when remediation email is sent
```json
{"type": "training_enrolled", "employee_email": "...", "campaign_id": "...",
 "token": "...", "is_simulation": true}
```

**Useful SPL queries:**
```
# All events
index=phishing_sim | table _time, type, employee_email, department, campaign_id

# Who clicked
index=phishing_sim sourcetype="phishing:click" | table _time, employee_email, department

# Click rate by department
index=phishing_sim (sourcetype="phishing:sent" OR sourcetype="phishing:click")
| stats count(eval(sourcetype="phishing:sent")) as sent,
        count(eval(sourcetype="phishing:click")) as clicked by department
| eval click_rate=round(clicked/sent*100,1)."%"
```

---

## License

MIT

**Built for the Splunk Agentic Ops Hackathon by [CodesByNeeraj](https://github.com/CodesByNeeraj)**
