from __future__ import annotations

import re
from typing import Literal
from pydantic import BaseModel, HttpUrl, Field, field_validator

# ── Request ────────────────────────────────────────────────────────────────
class AnalysisRequest(BaseModel):
    company_name:   str = Field(..., min_length=2, max_length=100, pattern=r"^[a-zA-Z0-9\s\.,\-\&]+$")
    company_url:    HttpUrl
    industry:       str = Field(..., max_length=50)
    years_inactive: int = Field(default=0, ge=0, le=20)
    report_language: Literal['en', 'es'] = 'en'
    analysis_depth: Literal['quick', 'standard', 'deep'] = 'standard'
    ai_temperature: float = Field(default=0.7, ge=0, le=1)
    stealth_mode: bool = False

    # Mapa de profundidad → número de resultados de búsqueda
    @property
    def search_results_count(self) -> int:
        return {'quick': 3, 'standard': 5, 'deep': 8}.get(self.analysis_depth, 5)

    @field_validator('company_name')
    @classmethod
    def check_prompt_injection(cls, v: str) -> str:
        """Bloquea patrones maliciosos antes de que lleguen a CrewAI / Llama 3."""
        dangerous_patterns = [
            r'(?i)ignore\s+previous',
            r'(?i)system:',
            r'(?i)jailbreak',
            r'```',
            r'<script>',
            r'(?i)DROP\s+TABLE',
            r'\{\{',
            r'\}\}',
            # patrones originales
            r'(?i)ignore\s+all',
            r'(?i)bypass',
            r'(?i)system\s+prompt',
            r'(?i)you\s+are\s+now',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError(
                    "🚨 Detectado posible intento de Prompt Injection. Solicitud rechazada."
                )
        return v

    @field_validator('company_url', mode='before')
    @classmethod
    def block_internal_urls(cls, v: str) -> str:
        """Rechaza IPs internas y localhost para evitar SSRF."""
        url_str = str(v).lower()
        internal_patterns = [
            r'localhost',
            r'127\.\d+\.\d+\.\d+',
            r'192\.168\.\d+\.\d+',
            r'10\.\d+\.\d+\.\d+',
            r'172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+',
        ]
        for pattern in internal_patterns:
            if re.search(pattern, url_str):
                raise ValueError(
                    "🚫 company_url no puede apuntar a direcciones internas o localhost."
                )
        return v


# ── Sub-modelos ─────────────────────────────────────────────────────────────
class ProductRecommendation(BaseModel):
    name:        str = ""
    description: str = ""
    roi_pitch:   str = ""
    pain_solved: str = ""

class NewsItem(BaseModel):
    title:   str = ""
    snippet: str = ""
    url:     str = ""
    source:  str = ""

# ── Response (completo — equivalente a las 5 páginas de Streamlit) ─────────
class AnalysisResponse(BaseModel):
    status:       str
    company_name: str
    industry:     str = ""
    lead_score:   int
    priority:     str = ""

    # Reporte de inteligencia (con tags [SECTION_X])
    intelligence_report: str

    # Sales Speech del Agente
    sales_speech: str = ""
    word_count:   int = 0

    # Auditoría / Compliance
    audit_passed: bool = False
    audit_notes:  str  = ""

    # Calidad de datos del scraper
    data_quality: str        = ""
    data_warning: str | None = None

    # Productos recomendados (RAG)
    products: list[ProductRecommendation] = []

    # Noticias recientes y fuentes
    recent_news:   list[NewsItem] = []
    sources:       list[str]      = []
    tech_keywords: str            = ""

    # Score factor breakdown (para ScoreBreakdown en el frontend)
    score_factors: dict = {}

