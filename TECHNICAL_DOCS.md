# KORHEX.AI — Technical Documentation

> v3.0 · Branch: `feature/platform-v3-enhancements`

This document covers the internal architecture, design patterns, API contracts, and all technical improvements introduced in platform version 3.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Modules](#backend-modules)
3. [OOP Design Patterns (v3)](#oop-design-patterns-v3)
4. [API Reference](#api-reference)
5. [Pydantic V2 Schema Hardening](#pydantic-v2-schema-hardening)
6. [SQLite Cache Layer](#sqlite-cache-layer)
7. [Async Parallel Scraper](#async-parallel-scraper)
8. [Frontend Architecture](#frontend-architecture)
9. [v3 Improvements Summary](#v3-improvements-summary)

---

## Architecture Overview

```
React 18 (Vite)
    │
    │  HTTP / SSE
    ▼
FastAPI (async)
    │
    ├── modules/scraper.py     ← asyncio.gather() parallel DDG search
    ├── modules/agents.py      ← CrewAI + Llama 3 (via run_in_executor)
    ├── modules/rag.py         ← Product portfolio matching
    ├── modules/database.py    ← SQLite WAL cache
    └── modules/agent.py       ← OOP patterns (Strategy, Singleton, Dataclass)
              │
              └── Ollama @ localhost:11434 (Llama 3 — local inference)
```

Zero external AI API calls. All inference is local.

---

## Backend Modules

### `main.py` — FastAPI Application

- **All blocking operations** (scraper, CrewAI, RAG) run inside `loop.run_in_executor(None, ...)` to avoid blocking the async event loop.
- **Cache-first strategy**: checks SQLite before triggering the scraper or agents.
- **Endpoints**:
  - `POST /api/v1/analyze` — Full pipeline (scrape → RAG → agents → score)
  - `POST /api/v1/analyze/stream` — Same pipeline but streams Llama 3 tokens via SSE
  - `POST /api/v1/export-pdf` — Generates a PDF report via ReportLab
  - `GET /health` — Returns Ollama status, loaded models, and cache stats

### `scraper.py` — Async Parallel Scraper

All 6 intelligence searches (strategy, tech, pain points, decision makers, financials, competitive) now run **simultaneously** using `asyncio.gather()`.

```python
tasks       = [_fetch_with_timeout(query, n, 10.0) for (_, query, n) in queries]
task_results = await asyncio.gather(*tasks)
```

Each query has a **10-second timeout** via `asyncio.wait_for()`. If a query times out, it returns an empty list instead of crashing the pipeline.

**Improvements over v2:**
- `region='wt-wt'` — forces neutral global results from DuckDuckGo
- Domain blacklist — filters out social media, calculators, translators
- Delay increased to `2.5–5.0s` — reduces rate-limiting risk

### `agents.py` — CrewAI Dual-Agent Pipeline

Two CrewAI agents run sequentially:
1. **Commercial Intelligence Analyst** — generates the 6-section intelligence report via direct Ollama call
2. **Senior HPE Sales Specialist** — generates the personalized sales pitch (150–350 words)

Both agents now use `OllamaClient().llm` (Singleton pattern) instead of creating a new LLM instance per request.

### `database.py` — SQLite Cache Layer

| Table | Purpose |
|-------|---------|
| `account_cache` | Raw scraper data, 24h TTL, hit counter |
| `analysis_cache` | Agent output (research + speech) keyed by company + years_inactive |
| `audit_log` | Tracks every analysis event (tokens used, processing time) |
| `lead_scores` | Historical lead scores per company |

Cache key = `MD5(company_name.lower() + company_url.lower() + industry.lower())`

WAL mode is enabled for concurrent read safety:
```python
conn.execute('PRAGMA journal_mode=WAL')
```

### `rag.py` — Product Portfolio Matching

Matches the scraped tech environment and industry against the internal HPE product catalog. Returns ranked product recommendations with ROI pitch and pain point mapping.

---

## OOP Design Patterns (v3)

All patterns are defined in `modules/agent.py`.

### Pattern A — Strategy Pattern (Scraper)

```python
class BaseScraper(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int) -> list[dict]: ...
    @abstractmethod
    def search_account(self, company_name, company_url, industry) -> dict: ...

class DuckDuckGoScraper(BaseScraper):
    # Current implementation

class AccountIntelligenceEngine:
    def __init__(self, scraper: BaseScraper):
        self._scraper = scraper  # Injected, swappable
```

New scrapers (e.g. `GoogleSearchScraper`, `BingAPIScraper`) can be plugged in without touching agent code.

### Pattern B — Singleton (Ollama LLM)

```python
class OllamaClient:
    _instance = None
    _llm      = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_llm()
        return cls._instance

    @property
    def llm(self): return self._llm
```

`OllamaClient().llm` returns the same LLM object every time — Llama 3 loads once.

### Pattern C — Result Dataclass

```python
@dataclass
class AnalysisResult:
    company_name:  str
    lead_score:    int
    priority:      str
    research:      str
    sales_speech:  str
    audit_passed:  bool
    data_quality:  str
    processing_ms: int
    products:      list[dict]
    sources:       list[str]

    @property
    def is_high_priority(self) -> bool:
        return self.lead_score >= 70

    @property
    def summary(self) -> str:
        return f"{self.company_name} — {self.lead_score}/100"
```

---

## API Reference

### `POST /api/v1/analyze`

**Request body:**
```json
{
  "company_name":    "Acme Corp",
  "company_url":     "https://acme.com",
  "industry":        "Technology",
  "years_inactive":  3,
  "report_language": "en",
  "analysis_depth":  "standard"
}
```

`analysis_depth` controls search result count:
- `quick` → 3 results per query
- `standard` → 5 results (default)
- `deep` → 8 results

**Response body (key fields):**
```json
{
  "status":               "success",
  "lead_score":           72,
  "priority":             "HIGH PRIORITY",
  "intelligence_report":  "[SECTION_1]...[SECTION_6]...",
  "sales_speech":         "...",
  "audit_passed":         true,
  "data_quality":         "HIGH",
  "score_factors": {
    "Inactivity Factor":    30,
    "Tech Initiatives":     20,
    "Pain Points Detected": 15,
    "Recent Activity":       7
  },
  "products":    [...],
  "recent_news": [...],
  "sources":     [...]
}
```

### `POST /api/v1/analyze/stream`

Returns `text/event-stream`. Events flow in this order:

```
data: {"step": "scraping", "status": "started"}
data: {"step": "scraping", "status": "done"}
data: {"step": "rag",      "status": "started"}
data: {"step": "rag",      "status": "done"}
data: {"step": "llm",      "status": "started"}
data: {"step": "llm",      "token": "Based"}
data: {"step": "llm",      "token": " on"}
...
data: {"step": "llm",      "status": "done"}
data: {"step": "complete"}
```

### `GET /health`

```json
{
  "status":         "ok",
  "service":        "KORHEX.AI — Backend API v2.1",
  "ollama":         { "running": true, "models": ["llama3:latest"] },
  "total_analyses": 47,
  "total_tokens":   94230,
  "cache":          { "description": "SQLite WAL cache — 24h TTL", "db_path": "backend/korhex.db" }
}
```

---

## Pydantic V2 Schema Hardening

### Prompt Injection Protection

`company_name` is validated against these patterns (case-insensitive):

```python
dangerous_patterns = [
    r'(?i)ignore\s+previous',
    r'(?i)system:',
    r'(?i)jailbreak',
    r'```',
    r'<script>',
    r'(?i)DROP\s+TABLE',
    r'\{\{', r'\}\}',
    r'(?i)ignore\s+all',
    r'(?i)bypass',
    r'(?i)system\s+prompt',
    r'(?i)you\s+are\s+now',
]
```

### SSRF Protection

`company_url` rejects internal addresses before any HTTP call is made:

- `localhost`
- `127.x.x.x`
- `192.168.x.x`
- `10.x.x.x`
- `172.16–31.x.x`

---

## SQLite Cache Layer

### Cache Flow

```
Request arrives
     │
     ├─ account_cache HIT? → skip scraper, use cached web_data
     │
     ├─ analysis_cache HIT? → skip CrewAI + Ollama, use cached research/speech
     │
     └─ MISS → run full pipeline → save both caches → return response
```

### Cache Key

```python
key = MD5(f"{name.lower()}:{url.lower()}:{industry.lower()}")
```

### TTL

24 hours. Expired entries are ignored but not automatically deleted (use `purge_company_data()` for GDPR-style removal).

---

## Async Parallel Scraper

### Before (v2 — sequential)

```
query 1 → wait ~5s
query 2 → wait ~5s
query 3 → wait ~5s
query 4 → wait ~5s
query 5 → wait ~5s
query 6 → wait ~5s
─────────────────────
Total: ~30s
```

### After (v3 — parallel)

```
query 1 ─┐
query 2 ─┤
query 3 ─┼─ asyncio.gather() → wait max ~8s
query 4 ─┤
query 5 ─┤
query 6 ─┘
```

Each query has a 10-second timeout. If one fails, the others continue.

---

## Frontend Architecture

All UI lives in a single file: `frontend/src/App.jsx`

### Component Tree

```
App
├── DashboardPage
│   ├── InvestigationForm      ← Ctrl+Enter shortcut, btn-execute ID
│   ├── PipelineTracker        ← Live step animations (v3)
│   ├── OverviewTab
│   │   ├── FreshnessIndicator ← Green/yellow/red data age (v3)
│   │   ├── CircularScore
│   │   └── ScoreBreakdown     ← 4 animated factor bars (v3)
│   ├── IntelligenceTab
│   ├── SpeechTab
│   ├── ProductsTab
│   ├── AuditTab
│   └── HistoryTable           ← Re-analyze + Copy Speech buttons (v3)
├── NewInvestigationPage       ← Same form + results layout
├── HistoryPage
└── UserPreferencesPage
```

### Key State Variables (App.jsx)

| State | Type | Purpose |
|-------|------|---------|
| `result` | object | Current analysis response (enriched with `_scoreFactors`, `_timestamp`) |
| `pipelineSteps` | object | Per-step status: `pending / active / done / error` |
| `history` | array | Last 10 analyses (stored in memory, not persisted) |
| `loading` | bool | True while fetch is in-flight |

---

## v3 Improvements Summary

| # | Improvement | File(s) Changed |
|---|------------|----------------|
| 1 | Parallel async scraper (`asyncio.gather` + 10s timeout) | `scraper.py` |
| 2 | FastAPI async + `run_in_executor` for all blocking calls | `main.py` |
| 2 | `/analyze/stream` SSE endpoint for live token streaming | `main.py` |
| 2 | `/health` returns Ollama status + cache stats | `main.py` |
| 3 | `get_cache_hit_rate()` function added | `database.py` |
| 4 | Strategy Pattern: `BaseScraper` / `DuckDuckGoScraper` / `AccountIntelligenceEngine` | `agent.py` |
| 4 | Singleton Pattern: `OllamaClient` | `agent.py`, `agents.py` |
| 4 | `AnalysisResult` dataclass with `is_high_priority` and `summary` properties | `agent.py` |
| 5 | Expanded prompt injection patterns | `schemas.py` |
| 5 | SSRF protection on `company_url` | `schemas.py` |
| 5 | `analysis_depth` Literal field (`quick / standard / deep`) | `schemas.py` |
| 5 | `report_language` changed to `Literal['en', 'es']` | `schemas.py` |
| 6 | Live pipeline tracker (5 steps with animations) | `App.jsx` |
| 7 | Score breakdown (4 animated factor bars) | `App.jsx` |
| 8a | Re-analyze and Copy Speech buttons in history | `App.jsx` |
| 8b | Ctrl+Enter keyboard shortcut for form submission | `App.jsx` |
| 8c | Data freshness indicator on Overview tab | `App.jsx` |
