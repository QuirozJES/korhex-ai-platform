# KORHEX.AI Enterprise 🛡️🤖

![KORHEX.AI](korhex-logo.png)

> **AI-powered B2B Account Intelligence Platform — 100% Local, Zero Data Leakage**

KORHEX.AI is an enterprise-grade platform that gives B2B sales teams deep commercial intelligence on target accounts — automatically. It uses a local AI pipeline to research public data, analyze tech environments, and generate personalized sales pitches, all without sending a single byte of sensitive information to any external cloud service.

---

## What does it do?

Given a company name and URL, KORHEX.AI runs a full intelligence pipeline and delivers:

- 🔍 **Account Intelligence** — Strategy, tech environment, pain points, decision makers, financial signals, and competitive context
- 🤖 **AI-Generated Sales Speech** — A personalized HPE enterprise pitch written by a CrewAI agent powered by Llama 3
- 📊 **Lead Score (0–100)** — A prioritization score based on inactivity, detected tech signals, and pain points
- 📦 **Product Recommendations** — Matched from an internal RAG product catalog
- 🔒 **Privacy Audit** — Full compliance check to ensure no data leaves the local environment

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Backend** | FastAPI + Pydantic V2 |
| **AI Agents** | CrewAI + Llama 3 via Ollama (local) |
| **Web Scraping** | DuckDuckGo Search (neutral region, domain filtered) |
| **Cache** | SQLite with WAL mode (24h TTL) |
| **LLM** | Llama 3 running on `localhost:11434` — no external API calls |

---

## Quick Start (Windows — 1 Click)

Make sure you have **Ollama running** with the `llama3` model pulled:

```powershell
ollama run llama3
```

Then launch both backend and frontend from the project root:

```powershell
.\start.ps1
```

The app will open automatically at **http://localhost:5173**

---

## Manual Setup

**Backend (FastAPI):**
```bash
cd backend
.\venv_backend\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (React + Vite):**
```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Create a file at `backend/.env`:

```env
# Optional: corporate proxy for web scraping
CORP_PROXY_URL=http://your-corporate-proxy:port

# JWT secret (skeleton, not enforced in dev mode)
JWT_SECRET=your_super_secret_jwt_key
```

---

## Prerequisites

- Python 3.12+
- Node.js 18+
- [Ollama](https://ollama.com/) with `llama3` model downloaded

---

## Key Features

- ⚡ **Parallel async scraping** — all 6 intelligence searches run simultaneously
- 🗄️ **SQLite cache** — avoids redundant scraping and LLM calls (24h TTL)
- 🔐 **Prompt injection protection** — input validation blocks common attack patterns
- 📡 **Streaming endpoint** — `/api/v1/analyze/stream` delivers live LLM tokens via SSE
- 🧠 **Singleton LLM** — Llama 3 is loaded once and reused across all requests
- 📋 **Live pipeline tracker** — the frontend shows real-time step-by-step progress

---

## Security

- All LLM inference runs at `127.0.0.1:11434` — never reaches external servers
- Internal/localhost URLs are blocked at the API level (SSRF protection)
- `.env`, `venv_backend/`, and `node_modules/` are excluded from version control

---

## Project Structure

```
korhex-ai-platform/
├── backend/
│   ├── main.py              # FastAPI app, endpoints, async pipeline
│   ├── models/schemas.py    # Pydantic V2 request/response models
│   ├── modules/
│   │   ├── scraper.py       # Async DuckDuckGo scraper (parallel)
│   │   ├── agents.py        # CrewAI dual-agent pipeline
│   │   ├── agent.py         # OOP patterns: Strategy, Singleton, Dataclass
│   │   ├── database.py      # SQLite cache layer (WAL mode)
│   │   ├── rag.py           # Product portfolio matching
│   │   └── pdf_report.py    # ReportLab PDF export
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── App.jsx          # React SPA (single file, all components)
├── start.ps1                # One-click launcher (Windows)
└── README.md
```

---

> For detailed technical documentation on architecture, OOP patterns, API contracts, and the v3 improvements, see [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md).
