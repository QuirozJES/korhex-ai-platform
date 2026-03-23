# backend/main.py
import asyncio
import io
import json
import time
import requests as _requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from models.schemas import AnalysisRequest, AnalysisResponse, ProductRecommendation, NewsItem
from modules.pdf_report import generate_report
from modules.scraper import search_account, calculate_net_new_score
from modules.agents import run_dual_agent_analysis
from modules.rag import get_relevant_products
from modules.database import (
    initialize_database,
    get_cached_account, save_account_cache,
    get_cached_analysis, save_analysis,
    log_audit_event, get_audit_summary,
)

# ── Inicializar DB al arranque ─────────────────────────────────────────────
initialize_database()

app = FastAPI(
    title="KORHEX.AI Enterprise API",
    description="Backend asíncrono para Account Intelligence Platform (Zero Data Leakage)",
    version="2.1.0"
)

# ── 1. CORS ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. JWT skeleton ──────────────────────────────────────────────────────────
def verify_jwt_token(token: str = "placeholder_token_ejemplo"):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
    return {"user": "analista_korhex", "role": "admin"}

# ── 3. Helpers ───────────────────────────────────────────────────────────────

def _get_ollama_status() -> dict:
    """Consulta el estado de Ollama sin bloquear el proceso si falla."""
    try:
        r = _requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m.get("name", "") for m in r.json().get("models", [])]
        return {"running": True, "models": models}
    except Exception:
        return {"running": False, "models": []}


def _build_response(
    company_name, industry, score, analysis, web_data, product_objs, years_inactive
) -> AnalysisResponse:
    """Construye la AnalysisResponse a partir de los artefactos del pipeline."""
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
        products=product_objs,
        recent_news=recent_news,
        sources=web_data.get("sources", [])[:10],
        tech_keywords=web_data.get("tech_keywords", ""),
        score_factors=score.get("factors", {}),
    )


# ── 4. Endpoint principal ─────────────────────────────────────────────────────
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_account(
    request: AnalysisRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Pipeline completo:
    1. Cache lookup (SQLite)
    2. Scraping vía DuckDuckGo — paralelo async
    3. RAG Semantic Matching
    4. Dual-Agent CrewAI sobre Llama 3 local — en executor para no bloquear el event loop
    5. Lead Scoring
    """
    t_start       = time.time()
    company_name  = request.company_name
    company_url   = str(request.company_url)
    industry      = request.industry
    years_inactive = request.years_inactive
    loop          = asyncio.get_event_loop()

    try:
        # ── STEP 0: Cache de cuenta ──────────────────────────────
        web_data = get_cached_account(company_name, company_url, industry)
        cache_hit_web = web_data is not None

        if not cache_hit_web:
            # Scraper corre en thread pool para no bloquear el event loop
            web_data = await loop.run_in_executor(
                None, search_account, company_name, company_url, industry
            )
            save_account_cache(company_name, company_url, industry, web_data)

        # ── STEP 1: RAG ──────────────────────────────────────────
        raw_products = await loop.run_in_executor(
            None, get_relevant_products, industry, web_data
        )
        product_objs = [
            ProductRecommendation(
                name=p.get("name", ""),
                description=p.get("description", ""),
                roi_pitch=p.get("roi_pitch", ""),
                pain_solved=p.get("pain_solved", ""),
            )
            for p in raw_products
        ]

        # ── STEP 2: Cache de análisis ─────────────────────────────
        cached_analysis = get_cached_analysis(company_name, company_url, industry, years_inactive)

        if cached_analysis:
            analysis = {
                "research_analysis": cached_analysis["research"],
                "sales_speech":      cached_analysis["sales_speech"],
                "word_count":        cached_analysis.get("word_count", 0),
                "audit_passed":      bool(cached_analysis["audit_passed"]),
                "audit_notes":       cached_analysis.get("audit_notes", ""),
                "estimated_tokens":  0,
            }
        else:
            # CrewAI es sync → ejecutar en thread pool para liberar el event loop
            analysis = await loop.run_in_executor(
                None,
                run_dual_agent_analysis,
                company_name, web_data, raw_products,
                years_inactive, "ACTIVE", request.report_language
            )
            save_analysis(
                company_name, company_url, industry, years_inactive,
                analysis["research_analysis"], analysis["sales_speech"],
                analysis.get("word_count", 0), analysis["audit_passed"], analysis["audit_notes"]
            )

        # ── STEP 3: Lead Scoring ─────────────────────────────────
        score = calculate_net_new_score(years_inactive, web_data)

        # ── Audit log ────────────────────────────────────────────
        processing_ms = int((time.time() - t_start) * 1000)
        log_audit_event(
            "analysis_complete",
            company_name,
            tokens=analysis.get("estimated_tokens", 0),
            processing_ms=processing_ms
        )

        return _build_response(
            company_name, industry, score, analysis, web_data, product_objs, years_inactive
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 5. Streaming endpoint ─────────────────────────────────────────────────────
@app.post("/api/v1/analyze/stream")
async def analyze_stream(
    request: AnalysisRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Streaming SSE: emite tokens de Llama 3 en tiempo real al frontend.
    Útil para mostrar el speech de ventas a medida que se genera.
    """
    company_name   = request.company_name
    company_url    = str(request.company_url)
    industry       = request.industry
    years_inactive = request.years_inactive
    loop           = asyncio.get_event_loop()

    async def event_generator():
        try:
            # Step 1: Scraping
            yield f"data: {json.dumps({'step': 'scraping', 'status': 'started'})}\n\n"
            web_data = get_cached_account(company_name, company_url, industry)
            if not web_data:
                web_data = await loop.run_in_executor(
                    None, search_account, company_name, company_url, industry
                )
                save_account_cache(company_name, company_url, industry, web_data)
            yield f"data: {json.dumps({'step': 'scraping', 'status': 'done'})}\n\n"

            # Step 2: RAG
            yield f"data: {json.dumps({'step': 'rag', 'status': 'started'})}\n\n"
            raw_products = await loop.run_in_executor(None, get_relevant_products, industry, web_data)
            yield f"data: {json.dumps({'step': 'rag', 'status': 'done'})}\n\n"

            # Step 3: Stream tokens from Ollama directly
            yield f"data: {json.dumps({'step': 'llm', 'status': 'started'})}\n\n"
            
            lang_name = "Spanish" if request.report_language == "es" else "English"
            product_context = "\n".join([
                f"- {p['name']}: {p['description']}" for p in raw_products
            ]) if raw_products else "No specific products."
            
            stream_prompt = (
                f"Write a professional HPE sales pitch for {company_name} "
                f"in {lang_name}. Industry: {industry}. "
                f"Recommended HPE solutions:\n{product_context}\n"
                f"Be concise, max 300 words."
            )

            def _stream_ollama():
                return _requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3", "prompt": stream_prompt, "stream": True},
                    stream=True,
                    timeout=180
                )

            response = await loop.run_in_executor(None, _stream_ollama)
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield f"data: {json.dumps({'step': 'llm', 'token': token})}\n\n"
                        if chunk.get("done"):
                            break
                    except Exception:
                        continue

            yield f"data: {json.dumps({'step': 'llm', 'status': 'done'})}\n\n"
            yield f"data: {json.dumps({'step': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── 6. Generación de PDF ──────────────────────────────────────────────────────
@app.post("/api/v1/export-pdf")
async def export_pdf(data: AnalysisResponse):
    """Recibe la respuesta completa y devuelve el reporte PDF generado por ReportLab."""
    try:
        analysis_data = data.model_dump()
        formatted_data = {
            "company_name":  analysis_data["company_name"],
            "company_url":   "N/A",
            "industry":      analysis_data["industry"],
            "years_inactive": 0,
            "score": {
                "total_score": analysis_data["lead_score"],
                "priority":    analysis_data["priority"],
                "is_net_new":  True
            },
            "analysis": {
                "research_analysis": analysis_data["intelligence_report"],
                "sales_speech":      analysis_data["sales_speech"],
                "audit_passed":      analysis_data["audit_passed"],
                "audit_notes":       analysis_data["audit_notes"],
                "word_count":        analysis_data["word_count"]
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


# ── 7. Health check mejorado ──────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """
    Retorna:
    - Estado de Ollama (modelos cargados)
    - Tasa de cache hits
    - Total de análisis ejecutados
    """
    loop = asyncio.get_event_loop()
    ollama_status  = await loop.run_in_executor(None, _get_ollama_status)
    audit_summary  = await loop.run_in_executor(None, get_audit_summary)

    total_analyses = audit_summary.get("total_analyses") or 0
    total_tokens   = audit_summary.get("total_tokens") or 0

    return {
        "status":          "ok",
        "service":         "KORHEX.AI — Backend API v2.1",
        "ollama":          ollama_status,
        "total_analyses":  total_analyses,
        "total_tokens":    total_tokens,
        "cache": {
            "description": "SQLite WAL cache — 24h TTL",
            "db_path":     "backend/korhex.db"
        }
    }


