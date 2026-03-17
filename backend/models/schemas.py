from pydantic import BaseModel, HttpUrl, Field, field_validator
import re

class AnalysisRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-zA-Z0-9\s\.\,\-\&]+$")
    company_url: HttpUrl
    industry: str = Field(..., max_length=50)
    years_inactive: int = Field(default=0, ge=0, le=20)

    @field_validator('company_name')
    @classmethod
    def check_prompt_injection(cls, v: str) -> str:
        """Bloquea patrones maliciosos en los inputs antes de que lleguen a CrewAI / Llama 3"""
        forbidden_patterns = [
            r"(?i)ignore\s+all", r"(?i)bypass", 
            r"(?i)system\s+prompt", r"(?i)you\s+are\s+now"
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, v):
                raise ValueError("🚨 Detectado posible intento de Prompt Injection. Solicitud rechazada.")
        return v

class AnalysisResponse(BaseModel):
    status: str
    company_name: str
    lead_score: int
    intelligence_report: str
