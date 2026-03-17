# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import io
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from models.schemas import AnalysisRequest, AnalysisResponse, ProductRecommendation, NewsItem
from modules.pdf_report import generate_report
from modules.scraper import search_account, calculate_net_new_score
from modules.agents import run_dual_agent_analysis
from modules.rag import get_relevant_products

app = FastAPI(
    title="KORHEX.AI Enterprise API",
    description="Backend asíncrono para Account Intelligence Platform (Zero Data Leakage)",
    version="2.0.0"
)

# ── 1. CORS ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. JWT skeleton ────────────────────────────────────────────────────────
def verify_jwt_token(token: str = "placeholder_token_ejemplo"):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
    return {"user": "analista_korhex", "role": "admin"}

# ── 3. Endpoint principal ──────────────────────────────────────────────────
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_account(
    request: AnalysisRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Pipeline completo (equivalente a las 5 páginas de Streamlit):
    1. Scraping vía DuckDuckGo (proxy corporativo)
    2. RAG: Semantic Matching con portafolio de productos
    3. Dual-Agent CrewAI sobre Llama 3 local (Ollama)
    4. Lead Scoring
    """
    try:
        company_name   = request.company_name
        company_url    = str(request.company_url)
        industry       = request.industry
        years_inactive = request.years_inactive

        # STEP 1 — Web Intelligence
        web_data = search_account(company_name, company_url, industry)

        # STEP 2 — RAG: Portfolio Matching
        raw_products = get_relevant_products(industry, web_data)
        products = [
            ProductRecommendation(
                name=p.get("name", ""),
                description=p.get("description", ""),
                roi_pitch=p.get("roi_pitch", ""),
                pain_solved=p.get("pain_solved", ""),
            )
            for p in raw_products
        ]

        # STEP 3 — Dual Agent CrewAI → Llama 3 local
        analysis = run_dual_agent_analysis(
            company_name, web_data, raw_products, years_inactive,
            report_language=request.report_language
        )

        # STEP 4 — Lead Scoring
        score = calculate_net_new_score(years_inactive, web_data)

        # STEP 5 — Noticias y fuentes del scraper
        recent_news = [
            NewsItem(
                title=n.get("title", ""),
                snippet=n.get("snippet", ""),
                url=n.get("url", ""),
                source=n.get("source", ""),
            )
            for n in web_data.get("recent_news", [])
        ]

        return AnalysisResponse(
            status="success",
            company_name=company_name,
            industry=industry,
            lead_score=score["total_score"],
            priority=score["priority"],
            intelligence_report=analysis["research_analysis"],
            sales_speech=analysis["sales_speech"],
            word_count=analysis.get("word_count", 0),
            audit_passed=analysis["audit_passed"],
            audit_notes=analysis["audit_notes"],
            data_quality=web_data.get("data_quality", "UNKNOWN"),
            data_warning=web_data.get("data_warning"),
            products=products,
            recent_news=recent_news,
            sources=web_data.get("sources", [])[:10],
            tech_keywords=web_data.get("tech_keywords", ""),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 4. Generación de PDF Legacy ────────────────────────────────────────────
@app.post("/api/v1/export-pdf")
async def export_pdf(data: AnalysisResponse):
    """
    Recibe la respuesta de análisis completa del frontend y devuelve
    el reporte PDF original generado por ReportLab.
    """
    try:
        # Convert Pydantic model back to dict for the legacy generator
        analysis_data = data.model_dump()
        
        # Restructure specifically for how generate_report expects it:
        # It expects {"company_name": "...", "score": {"total_score": 58, "priority": "..."}, "analysis": {"research_analysis": "...", "sales_speech": "...", ...}}
        formatted_data = {
            "company_name": analysis_data["company_name"],
            "company_url": "N/A", # URL is not passed back in standard response, but PDF handles "N/A"
            "industry": analysis_data["industry"],
            "years_inactive": 0, # Not strictly in response, defaults to 0
            "score": {
                "total_score": analysis_data["lead_score"],
                "priority": analysis_data["priority"],
                "is_net_new": True # Simplified
            },
            "analysis": {
                "research_analysis": analysis_data["intelligence_report"],
                "sales_speech": analysis_data["sales_speech"],
                "audit_passed": analysis_data["audit_passed"],
                "audit_notes": analysis_data["audit_notes"],
                "word_count": analysis_data["word_count"]
            },
            "products": analysis_data["products"]
        }

        pdf_bytes = generate_report(formatted_data)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=KORHEX_{data.company_name.replace(' ', '_')}_Report.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation Error: {str(e)}")

# ── 5. Health check ────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "KORHEX.AI — Backend API v2.0"}
