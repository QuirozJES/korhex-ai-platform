from pydantic import BaseModel, HttpUrl, Field, field_validator
import re

# ── Request ────────────────────────────────────────────────────────────────
class AnalysisRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-zA-Z0-9\s\.\,\-\&]+$")
    company_url: HttpUrl
    industry: str = Field(..., max_length=50)
    years_inactive: int = Field(default=0, ge=0, le=20)
    report_language: str = Field(default='en', pattern='^(en|es)$')

    @field_validator('company_name')
    @classmethod
    def check_prompt_injection(cls, v: str) -> str:
        """Bloquea patrones maliciosos antes de que lleguen a CrewAI / Llama 3"""
        forbidden_patterns = [
            r"(?i)ignore\s+all", r"(?i)bypass",
            r"(?i)system\s+prompt", r"(?i)you\s+are\s+now"
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, v):
                raise ValueError("🚨 Detectado posible intento de Prompt Injection. Solicitud rechazada.")
        return v

# ── Sub-modelos ─────────────────────────────────────────────────────────────
class ProductRecommendation(BaseModel):
    name: str = ""
    description: str = ""
    roi_pitch: str = ""
    pain_solved: str = ""

class NewsItem(BaseModel):
    title: str = ""
    snippet: str = ""
    url: str = ""
    source: str = ""

# ── Response (completo — equivalente a las 5 páginas de Streamlit) ─────────
class AnalysisResponse(BaseModel):
    status: str
    company_name: str
    industry: str = ""
    lead_score: int
    priority: str = ""

    # Reporte de inteligencia (con tags [SECTION_X])
    intelligence_report: str

    # Sales Speech del Agente
    sales_speech: str = ""
    word_count: int = 0

    # Auditoría / Compliance
    audit_passed: bool = False
    audit_notes: str = ""

    # Calidad de datos del scraper
    data_quality: str = ""
    data_warning: str | None = None

    # Productos recomendados (RAG)
    products: list[ProductRecommendation] = []

    # Noticias recientes y fuentes
    recent_news: list[NewsItem] = []
    sources: list[str] = []
    tech_keywords: str = ""
