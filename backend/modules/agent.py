"""
backend/modules/agent.py — OOP Patterns para KORHEX.AI

PATTERN A: Strategy Pattern → BaseScraper / DuckDuckGoScraper / AccountIntelligenceEngine
PATTERN B: Singleton       → OllamaClient (LLM se instancia UNA sola vez)
PATTERN C: Result Dataclass → AnalysisResult
"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# ─── PATTERN C — AnalysisResult Dataclass ────────────────────
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
    products:      list[dict] = field(default_factory=list)
    sources:       list[str]  = field(default_factory=list)
    word_count:    int        = 0
    audit_notes:   str        = ""

    @property
    def is_high_priority(self) -> bool:
        """True si el lead score supera o iguala 70."""
        return self.lead_score >= 70

    @property
    def summary(self) -> str:
        """Resumen de una línea para logging / UI."""
        return f"{self.company_name} — {self.lead_score}/100 ({self.priority})"


# ─── PATTERN A — Strategy Pattern: BaseScraper ───────────────

class BaseScraper(ABC):
    """Interfaz abstracta para scrapers de inteligencia de cuentas."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Executes a single search and returns normalized result items."""
        ...

    @abstractmethod
    def search_account(
        self,
        company_name: str,
        company_url: str = "",
        industry: str = "Technology",
    ) -> dict:
        """Full account intelligence pipeline. Returns the structured web_data dict."""
        ...


class DuckDuckGoScraper(BaseScraper):
    """
    Implementación concreta de BaseScraper usando DuckDuckGo.
    Delega al módulo scraper.py existente para mantener DRY.
    """

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        from modules.scraper import _fetch_with_timeout
        return await _fetch_with_timeout(query, max_results, timeout=10.0)

    def search_account(
        self,
        company_name: str,
        company_url: str = "",
        industry: str = "Technology",
    ) -> dict:
        from modules.scraper import search_account
        return search_account(company_name, company_url, industry)


class AccountIntelligenceEngine:
    """
    Motor principal que recibe un BaseScraper via dependency injection.
    Permite intercambiar el scraper sin tocar el código de agentes.
    """

    def __init__(self, scraper: BaseScraper):
        self._scraper = scraper

    def gather_intelligence(
        self,
        company_name: str,
        company_url: str = "",
        industry: str = "Technology",
    ) -> dict:
        """Delega la recolección de inteligencia al scraper inyectado."""
        return self._scraper.search_account(company_name, company_url, industry)

    async def gather_intelligence_async(
        self,
        company_name: str,
        company_url: str = "",
        industry: str = "Technology",
    ) -> dict:
        """Versión async: corre gather_intelligence en thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._scraper.search_account, company_name, company_url, industry
        )


# ─── PATTERN B — Singleton: OllamaClient ─────────────────────

class OllamaClient:
    """
    Singleton que mantiene una única instancia del LLM de Ollama.
    El modelo se carga UNA SOLA VEZ en memoria; todas las peticiones reutilizan
    la misma conexión evitando reloadings costosos.

    Uso:
        llm = OllamaClient().llm
    """
    _instance: OllamaClient | None = None
    _llm: Any = None

    def __new__(cls) -> OllamaClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_llm()
        return cls._instance

    def _init_llm(self) -> None:
        try:
            from crewai import LLM
            self._llm = LLM(
                model="ollama/llama3",
                base_url="http://localhost:11434"
            )
        except Exception as e:
            self._llm = None
            print(f"[OllamaClient] Warning: could not initialize LLM — {e}")

    @property
    def llm(self) -> Any:
        return self._llm