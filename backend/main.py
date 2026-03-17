# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from models.schemas import AnalysisRequest, AnalysisResponse

app = FastAPI(
    title="KORHEX.AI Enterprise API",
    description="Backend asíncrono para Account Intelligence Platform (Zero Data Leakage)",
    version="2.0.0"
)

# ── 1. CONFIGURACIÓN CORS (Comunicación con React) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Puerto por defecto de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 2. ESQUELETO DE AUTENTICACIÓN JWT ──
def verify_jwt_token(token: str = "placeholder_token_ejemplo"):
    # IMPORTANTE: Aquí deberías verificar contra el header 'Authorization: Bearer <token>'
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no válido")
    return {"user": "analista_korhex", "role": "admin"}

# ── 3. ENDPOINTS ──
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_account(request: AnalysisRequest, current_user: dict = Depends(verify_jwt_token)):
    """
    Inicia la orquestación asíncrona de CrewAI para buscar en Tavily y razonar con Llama 3.
    """
    try:
        # AQUI VA TU LÓGICA DE CREWAI
        # En la vida real, derivarías el llamado a: await orchestrator.run_agents(request)
        
        # Simulamos el procesamiento asíncrono para el frontend (3 segundos de inferencia local ficticia)
        await asyncio.sleep(3) 
        
        return AnalysisResponse(
            status="success",
            company_name=request.company_name,
            lead_score=87,
            intelligence_report=(
                f"La empresa {request.company_name} requiere una aproximación "
                f"enfocada en optimización de costos en su sector ({request.industry}). "
                "Análisis inferido exitosamente en local."
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "KORHEX AI - Backend API Runner"}
