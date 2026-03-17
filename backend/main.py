# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()  # Carga CORP_PROXY_URL y JWT_SECRET desde backend/.env

from models.schemas import AnalysisRequest, AnalysisResponse
from modules.scraper import search_account, calculate_net_new_score
from modules.agents import run_dual_agent_analysis
from modules.rag import get_relevant_products

app = FastAPI(
    title="KORHEX.AI Enterprise API",
    description="Backend asíncrono para Account Intelligence Platform (Zero Data Leakage)",
    version="2.0.0"
)

# ── 1. CONFIGURACIÓN CORS (Comunicación con React en Vite) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. ESQUELETO DE AUTENTICACIÓN JWT ──────────────────────────────────────
def verify_jwt_token(token: str = "placeholder_token_ejemplo"):
    # TODO: Verificar 'Authorization: Bearer <token>' del header real
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no válido"
        )
    return {"user": "analista_korhex", "role": "admin"}

# ── 3. ENDPOINT PRINCIPAL — Análisis de Cuenta ─────────────────────────────
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_account(
    request: AnalysisRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Pipeline completo:
    1. Scraping vía DuckDuckGo (proxy corporativo)
    2. RAG: Semantic Matching con portafolio de productos
    3. Dual-Agent CrewAI (Account Executive + Compliance Agent) sobre Llama 3 local
    """
    try:
        company_name    = request.company_name
        company_url     = str(request.company_url)
        industry        = request.industry
        years_inactive  = request.years_inactive

        # STEP 1 — Web Intelligence Retrieval (DuckDuckGo + proxy corporativo)
        web_data = search_account(company_name, company_url, industry)

        # STEP 2 — Portfolio Semantic Matching (RAG local)
        products = get_relevant_products(industry, web_data)

        # STEP 3 — Dual Agent CrewAI → Llama 3 local (Ollama en 127.0.0.1:11434)
        analysis = run_dual_agent_analysis(
            company_name, web_data, products, years_inactive
        )

        # STEP 4 — Lead Scoring
        score = calculate_net_new_score(years_inactive, web_data)

        return AnalysisResponse(
            status="success",
            company_name=company_name,
            lead_score=score["total_score"],
            intelligence_report=analysis["research_analysis"],
            sales_speech=analysis["sales_speech"],
            audit_passed=analysis["audit_passed"],
            audit_notes=analysis["audit_notes"],
            priority=score["priority"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 4. HEALTH CHECK ────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "KORHEX.AI — Backend API v2.0"}
