# KORHEX.AI Enterprise 🛡️🤖

![KORHEX.AI](korhex-logo.png)

**KORHEX.AI** is an **Enterprise Account Intelligence** platform strictly designed around a **"Zero Data Leakage"** architecture. It performs deep B2B account analysis operating entirely locally, ensuring that sensitive and strategic information never leaves the corporate environment.

## 🏗️ Technical Architecture (v2.0)

The system has been completely refactored from a monolithic proof-of-concept into a scalable, enterprise-grade decoupled architecture:

### 1. Frontend (React 18 + Vite + Tailwind CSS)
- **UI/UX:** A modern, dark-themed dashboard tailored for Account Managers, featuring 5 distinct Intelligence Tabs (`Overview`, `Intelligence`, `Sales Speech`, `Products`, `Privacy Audit`).
- **State Management:** Fully functional local history tracking and user preferences (Name, Industry defaults, Target Language).
- **Network:** Asynchronous data fetching equipped with `AbortController` to cancel in-flight agent executions gracefully.

### 2. Backend (FastAPI + Pydantic)
- **Core Framework:** High-performance, asynchronous REST API powered by FastAPI.
- **Data Validation:** Strict input/output validation and Prompt Injection prevention mechanisms using **Pydantic V2**.
- **Auth Skeleton:** Prepared for enterprise JWT integration.

### 3. AI Orchestration (CrewAI + Llama 3)
- **Multi-Agent System:** Employs `CrewAI` to run sequential reasoning agents (Intelligence Analyst, Senior Sales Specialist).
- **Zero Data Leakage Execution:** Uses **Llama 3** running locally via **Ollama**. *No external AI APIs (OpenAI, Anthropic) are used.*
- **Corporate Scraping:** Swapped public API scrapers (Tavily) for `duckduckgo-search` strictly routed through an internal corporate proxy (`CORP_PROXY_URL`) to ensure complete search anonymity.

---

## 💾 Data Structures & Schemas

The application enforces a strict data contract between the frontend and backend using Pydantic:

### `AnalysisRequest`
Validates inputs to prevent prompt injection and handle default configurations:
- `company_name`: `str` (Regex validated against injections)
- `company_url`: `HttpUrl`
- `industry`: `str`
- `years_inactive`: `int` (Range: 0-20)
- `report_language`: `str` (`en` or `es` — Injected directly into Llama 3 system prompts)

### `AnalysisResponse`
A comprehensive JSON payload unifying the output of the scraper, RAG portfolio matching, and CrewAI agents:
- `company_name` & `lead_score`
- `data_quality` & `data_warning`
- `intelligence_report` (Formatted with `[SECTION_N]` parsing tags for the UI)
- `sales_speech` (Limited to 240 words via Auditor Agent)
- `audit_passed` & `audit_notes`
- `products` (Array of ROI-focused product mappings)
- `recent_news` & `sources`

---

## 🚀 Setup & Execution

### Prerequisites
- Node.js (v18+)
- Python (v3.12+)
- Ollama running locally with `llama3` pulled (`ollama run llama3`)

### Environment Variables (`backend/.env`)
```env
CORP_PROXY_URL=http://your-corporate-proxy:port
JWT_SECRET=your_super_secret_jwt_key
```

### 1-Click Startup (Windows)
Run the provided PowerShell script from the root directory to automatically launch both the FastAPI backend and the Vite frontend:
```powershell
.\start.ps1
```

### Manual Startup
**Backend:**
```bash
cd backend
.\venv_backend\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Security Policies
- **Strict Network Isolation:** All LLM reasoning occurs on `127.0.0.1:11434`.
- **Git Hygiene:** Dependencies (`node_modules`, `venv_backend`), environment variables (`.env`), and OS artifacts are properly `.gitignore`d.
