# KORHEX.AI — Documentación Técnica

> Versión 3.0 · Rama: `feature/platform-v3-enhancements`

Esta documentación explica en detalle cómo funciona la plataforma por dentro: su arquitectura, los módulos del backend, los patrones de diseño utilizados, el contrato de la API y todas las mejoras introducidas en la versión 3.

---

## Tabla de Contenidos

1. [Visión General de la Arquitectura](#1-visión-general-de-la-arquitectura)
2. [Módulos del Backend](#2-módulos-del-backend)
3. [Patrones de Diseño OOP (v3)](#3-patrones-de-diseño-oop-v3)
4. [Referencia de la API](#4-referencia-de-la-api)
5. [Validaciones con Pydantic V2](#5-validaciones-con-pydantic-v2)
6. [Sistema de Caché SQLite](#6-sistema-de-caché-sqlite)
7. [Scraper Asíncrono Paralelo](#7-scraper-asíncrono-paralelo)
8. [Arquitectura del Frontend](#8-arquitectura-del-frontend)
9. [Resumen de Mejoras v3](#9-resumen-de-mejoras-v3)

---

## 1. Visión General de la Arquitectura

El sistema está dividido en dos capas principales que se comunican a través de HTTP:

```
┌──────────────────────────────────────────┐
│         FRONTEND (React 18 + Vite)       │
│  El usuario llena el formulario y lanza  │
│  el análisis. Muestra resultados en tabs │
└────────────────┬─────────────────────────┘
                 │ HTTP / SSE (Server-Sent Events)
                 ▼
┌──────────────────────────────────────────┐
│         BACKEND (FastAPI — async)        │
│                                          │
│  1. scraper.py  → Búsqueda web en DDG   │
│  2. rag.py      → Matching de productos  │
│  3. agents.py   → Agentes CrewAI / Llama │
│  4. database.py → Caché SQLite WAL       │
│  5. agent.py    → Patrones OOP           │
└────────────────┬─────────────────────────┘
                 │ HTTP local
                 ▼
┌──────────────────────────────────────────┐
│     OLLAMA @ localhost:11434             │
│     Modelo: Llama 3 (ejecución local)    │
│     ⚠️ Cero llamadas a APIs externas     │
└──────────────────────────────────────────┘
```

**Principio fundamental:** Todo el razonamiento de IA ocurre dentro de la máquina local. Ningún dato sensible viaja a servidores externos. Esto es lo que llamamos arquitectura **"Zero Data Leakage"**.

---

## 2. Módulos del Backend

### `main.py` — Aplicación FastAPI

Es el punto de entrada del backend. Define los endpoints y orquesta todo el pipeline de análisis.

**Decisión de diseño clave:** Para que FastAPI funcione correctamente de forma asíncrona, todas las funciones bloqueantes (scraper, agentes CrewAI) se envuelven con `loop.run_in_executor()`. Esto evita que una llamada lenta congele todo el servidor mientras atiende otras peticiones.

```python
# En lugar de llamar directamente (bloquea el event loop):
web_data = search_account(company_name, ...)

# Se llama con executor para no bloquear:
web_data = await loop.run_in_executor(None, search_account, company_name, ...)
```

**Endpoints disponibles:**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/analyze` | POST | Pipeline completo de análisis |
| `/api/v1/analyze/stream` | POST | Misma lógica pero transmite tokens de Llama 3 en vivo |
| `/api/v1/export-pdf` | POST | Genera un PDF con ReportLab |
| `/health` | GET | Estado de Ollama + estadísticas de caché |

---

### `scraper.py` — Scraper Web Asíncrono

Se encarga de buscar información pública sobre una empresa en DuckDuckGo y organizarla en 6 categorías de inteligencia:

1. **Strategy Background** — Estrategia corporativa e iniciativas recientes
2. **Tech Environment** — Infraestructura tecnológica actual
3. **Pain Points** — Problemas y retos de TI identificados
4. **Decision Makers** — Directivos y tomadores de decisiones
5. **Financial Signals** — Señales financieras (ingresos, inversiones)
6. **Competitive Context** — Posición en el mercado y competidores

**Mejoras aplicadas en v3:**
- `region='wt-wt'` fuerza resultados globales neutros (evita resultados localizados basura)
- Lista negra de dominios que filtra redes sociales, calculadoras y traductores
- Delay aumentado a `2.5–5.0s` entre peticiones para evitar bloqueos de DuckDuckGo

---

### `agents.py` — Pipeline de Agentes CrewAI

Contiene la lógica de los dos agentes de IA que se ejecutan de forma secuencial:

**Agente 1 — Commercial Intelligence Analyst**
Recibe todos los datos del scraper y genera un reporte estructurado con 6 secciones. Usa una llamada directa a Ollama (más rápido y controlable que pasar por CrewAI).

**Agente 2 — Senior HPE Sales Specialist**
Toma el contexto del análisis y genera un pitch de ventas personalizado de entre 150 y 350 palabras, incluyendo un "Top 5 HPE Solutions" con los productos más relevantes para esa cuenta.

Si CrewAI falla (por ejemplo, si `litellm` no está instalado), hay un fallback que llama directamente a Ollama, garantizando que el sistema no se rompa.

---

### `database.py` — Caché SQLite

Base de datos local que evita repetir trabajo costoso (búsquedas web + llamadas al LLM).

**Tablas:**

| Tabla | ¿Qué guarda? |
|-------|--------------|
| `account_cache` | Datos del scraper por empresa. Expiran en 24h. Tiene contador de hits. |
| `analysis_cache` | Resultado de los agentes (reporte + speech), único por empresa + años inactivos. |
| `audit_log` | Historial de cada análisis: tokens usados, tiempo de procesamiento, costo estimado. |
| `lead_scores` | Puntuaciones históricas de leads por empresa. |

La clave de cada registro es un hash MD5 calculado así:
```
clave = MD5("nombre_empresa:url_empresa:industria")
```

Esto garantiza que dos empresas distintas con el mismo nombre (pero diferente URL) no colisionen en el caché.

---

### `rag.py` — Matching de Portafolio de Productos

Compara la industria y el entorno tecnológico detectado contra el catálogo interno de productos HPE. Devuelve los productos más relevantes con su propuesta de ROI y el problema que resuelven, para que los agentes puedan incluirlos en el pitch.

---

### `agent.py` — Patrones OOP

Contiene los tres patrones de diseño introducidos en la v3. Se explican en detalle en la sección siguiente.

---

## 3. Patrones de Diseño OOP (v3)

### Patrón A — Strategy (Scraper intercambiable)

**Problema que resuelve:** Antes, si se quería cambiar DuckDuckGo por otro motor de búsqueda, había que modificar directamente el código de los agentes. Eso es una mala práctica porque el agente no debería saber de dónde vienen los datos.

**Solución:** Se define una clase abstracta `BaseScraper` que actúa como contrato. Cualquier scraper concreto que la implemente puede ser inyectado en el motor principal sin tocar nada más.

```python
class BaseScraper(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int) -> list[dict]: ...

class DuckDuckGoScraper(BaseScraper):
    # Implementación actual con DDG

class AccountIntelligenceEngine:
    def __init__(self, scraper: BaseScraper):
        # Recibe cualquier scraper → desacoplado
        self._scraper = scraper
```

Si en el futuro se quiere usar Google Search API o Bing, solo hay que crear `GoogleScraper(BaseScraper)` y pasárselo al engine. Todo lo demás queda igual.

---

### Patrón B — Singleton (Instancia única del LLM)

**Problema que resuelve:** Antes, en cada petición de análisis se creaba un nuevo objeto `LLM(model="ollama/llama3")`. Aunque Ollama no recarga el modelo en disco cada vez, este comportamiento desperdicia recursos y puede causar problemas de concurrencia.

**Solución:** `OllamaClient` implementa el patrón Singleton: el objeto LLM se crea una sola vez en la primera instanciación y todas las llamadas subsiguientes reutilizan exactamente el mismo objeto.

```python
class OllamaClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:              # Primera vez → crear
            cls._instance = super().__new__(cls)
            cls._instance._init_llm()
        return cls._instance                   # Siempre regresa el mismo

# En agents.py:
mi_llm = OllamaClient().llm   # Mismo objeto en toda la vida del proceso
```

---

### Patrón C — Dataclass de Resultado Tipado

**Problema que resuelve:** Antes, todas las funciones de agentes devolvían diccionarios Python sin estructura fija. Eso hace el código difícil de mantener y propenso a errores de tipo (un campo mal escrito no lo detecta nadie hasta el runtime).

**Solución:** Se define `AnalysisResult` como un dataclass con tipos explícitos y propiedades calculadas.

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

    @property
    def is_high_priority(self) -> bool:
        return self.lead_score >= 70  # Lógica centralizada aquí

    @property
    def summary(self) -> str:
        return f"{self.company_name} — {self.lead_score}/100"
```

Ahora cualquier función que llame al agente sabe exactamente qué campos esperar.

---

## 4. Referencia de la API

### `POST /api/v1/analyze`

**Cuerpo de la petición:**
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

El campo `analysis_depth` controla cuántos resultados de búsqueda se obtienen por query:
- `quick` → 3 resultados (más rápido, menos datos)
- `standard` → 5 resultados (balance recomendado)
- `deep` → 8 resultados (más completo, más lento)

**Respuesta (campos principales):**
```json
{
  "status":               "success",
  "lead_score":           72,
  "priority":             "HIGH PRIORITY",
  "intelligence_report":  "[SECTION_1]...[SECTION_6]...",
  "sales_speech":         "...",
  "audit_passed":         true,
  "audit_notes":          "Speech approved: 287 words.",
  "data_quality":         "HIGH",
  "data_warning":         null,
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

El `intelligence_report` usa etiquetas `[SECTION_X]` que el frontend parsea para mostrar cada sección en su propia tarjeta visual.

---

### `POST /api/v1/analyze/stream`

Este endpoint establece una conexión SSE (Server-Sent Events) y transmite el progreso del pipeline en tiempo real. Útil para mostrar al usuario qué está pasando paso a paso.

Los eventos llegan en este orden:
```
data: {"step": "scraping", "status": "started"}
data: {"step": "scraping", "status": "done"}
data: {"step": "rag",      "status": "started"}
data: {"step": "rag",      "status": "done"}
data: {"step": "llm",      "status": "started"}
data: {"step": "llm",      "token": "Based"}
data: {"step": "llm",      "token": " on"}
  ... (un evento por cada token de Llama 3)
data: {"step": "llm",      "status": "done"}
data: {"step": "complete"}
```

---

### `GET /health`

Devuelve el estado completo del sistema. Útil para monitoreo o para verificar que Ollama está corriendo antes de lanzar un análisis.

```json
{
  "status":         "ok",
  "service":        "KORHEX.AI — Backend API v2.1",
  "ollama": {
    "running": true,
    "models":  ["llama3:latest"]
  },
  "total_analyses": 47,
  "total_tokens":   94230,
  "cache": {
    "description": "SQLite WAL cache — 24h TTL",
    "db_path":     "backend/korhex.db"
  }
}
```

---

## 5. Validaciones con Pydantic V2

### Protección contra Prompt Injection

Un atacante podría intentar manipular el LLM enviando instrucciones maliciosas dentro del nombre de la empresa. El validador de Pydantic bloquea estos intentos antes de que el dato llegue a los agentes:

```python
# Patrones que se rechazan automáticamente:
dangerous_patterns = [
    r'(?i)ignore\s+previous',   # "ignore previous instructions"
    r'(?i)system:',             # inyección de system prompt
    r'(?i)jailbreak',           # jailbreak explícito
    r'```',                     # bloques de código
    r'<script>',                # XSS
    r'(?i)DROP\s+TABLE',        # SQL injection
    r'\{\{', r'\}\}',           # template injection
]
```

Si cualquiera de estos patrones aparece en `company_name`, la API devuelve un error 422 inmediatamente.

### Protección SSRF en la URL

SSRF (Server-Side Request Forgery) ocurre cuando un atacante hace que el servidor haga peticiones a direcciones internas que no debería poder alcanzar. El validador de `company_url` rechaza cualquier dirección local antes de que el sistema intente conectarse:

```
localhost       → ❌ bloqueado
127.0.0.1       → ❌ bloqueado
192.168.1.50    → ❌ bloqueado
10.0.0.1        → ❌ bloqueado
172.16.0.1      → ❌ bloqueado
https://acme.com → ✅ permitido
```

---

## 6. Sistema de Caché SQLite

### ¿Por qué SQLite con WAL?

SQLite en modo WAL (Write-Ahead Logging) permite que múltiples lecturas ocurran simultáneamente sin bloquearse entre sí. Es perfecto para este caso de uso donde hay muchas lecturas de caché y escrituras ocasionales.

### Flujo de decisión del pipeline

```
Llega una petición de análisis
         │
         ▼
¿Hay datos del scraper en account_cache? (no expirados)
    ├── SÍ → Usar datos del caché, saltar scraper (ahorro: ~8–30s)
    └── NO → Ejecutar scraper + guardar en account_cache
         │
         ▼
¿Hay análisis de agentes en analysis_cache?
    ├── SÍ → Usar análisis del caché, saltar CrewAI + Llama 3 (ahorro: ~60–180s)
    └── NO → Ejecutar agentes + guardar en analysis_cache
         │
         ▼
Calcular Lead Score → Registrar en audit_log → Devolver respuesta
```

### TTL y Expiración

La TTL (Time To Live) del caché es de 24 horas. Una entrada expirada no se borra automáticamente pero tampoco se usa — el sistema simplemente la ignora y vuelve a buscar datos frescos.

Para eliminar datos específicos de una empresa (por ejemplo por motivos de privacidad GDPR), existe la función `purge_company_data()` que borra las filas de `account_cache` y `lead_scores`, y anonimiza el nombre en `audit_log`.

---

## 7. Scraper Asíncrono Paralelo

### El problema en la v2

En la versión anterior, las 6 búsquedas de inteligencia se ejecutaban **en secuencia**, una detrás de otra. Cada búsqueda esperaba ~5 segundos por la respuesta de DuckDuckGo más el delay anti-rate-limiting:

```
Búsqueda 1 (Strategy)  ──── 5s
Búsqueda 2 (Tech)      ──────────── 5s
Búsqueda 3 (Pain)      ─────────────────── 5s
Búsqueda 4 (Makers)    ──────────────────────── 5s
Búsqueda 5 (Financial) ───────────────────────────── 5s
Búsqueda 6 (Compet.)   ────────────────────────────────── 5s
                                                        ≈ 30s total
```

### La solución en la v3

Todas las búsquedas se lanzan **al mismo tiempo** con `asyncio.gather()`. El tiempo total es el de la búsqueda más lenta (no la suma de todas):

```
Búsqueda 1 (Strategy)  ────────────┐
Búsqueda 2 (Tech)      ────────────┤
Búsqueda 3 (Pain)      ────────────┤ asyncio.gather()
Búsqueda 4 (Makers)    ────────────┤ ≈ 8s total
Búsqueda 5 (Financial) ────────────┤
Búsqueda 6 (Compet.)   ────────────┘
```

Adicionalmente, cada búsqueda tiene un **timeout de 10 segundos**. Si alguna consulta tarda demasiado (por ejemplo por problemas de red), se cancela y devuelve una lista vacía en lugar de bloquear todo el proceso.

```python
async def _fetch_with_timeout(query, max_results, timeout=10.0):
    try:
        return await asyncio.wait_for(_async_ddg_search(query, max_results), timeout=timeout)
    except asyncio.TimeoutError:
        return []   # Falla silenciosa, el pipeline continúa
```

---

## 8. Arquitectura del Frontend

Todo el frontend está en un solo archivo: `frontend/src/App.jsx`. Esto es intencional para mantener el proyecto portable y fácil de desplegar.

### Árbol de componentes

```
App (estado global)
├── DashboardPage
│   ├── InvestigationForm      ← Formulario con atajo Ctrl+Enter
│   ├── PipelineTracker        ← Tracker de 5 pasos en tiempo real (v3)
│   ├── [Pestañas de resultado]
│   │   ├── OverviewTab
│   │   │   ├── FreshnessIndicator  ← Semáforo de frescura de datos (v3)
│   │   │   ├── CircularScore       ← Donut con el puntaje
│   │   │   └── ScoreBreakdown      ← 4 barras de progreso por factor (v3)
│   │   ├── IntelligenceTab    ← Secciones del reporte parseadas
│   │   ├── SpeechTab          ← Pitch de ventas + estado de auditoría
│   │   ├── ProductsTab        ← Productos recomendados por RAG
│   │   └── AuditTab           ← Fuentes usadas + estado de privacidad
│   └── HistoryTable           ← Historial con Re-analyze + Copy Speech (v3)
├── NewInvestigationPage       ← Mismo formulario y resultados en layout diferente
├── HistoryPage
└── UserPreferencesPage        ← Idioma, industria por defecto, nombre de usuario
```

### Variables de estado principales en `App.jsx`

| Variable | Tipo | ¿Para qué sirve? |
|----------|------|-----------------|
| `result` | objeto | Última respuesta de la API + metadatos `_scoreFactors` y `_timestamp` |
| `pipelineSteps` | objeto | Estado de cada paso: `pending / active / done / error` |
| `history` | array | Últimas 10 investigaciones (en memoria, no persistidas) |
| `loading` | bool | `true` mientras hay una petición en vuelo |
| `formData` | objeto | Valores actuales del formulario de investigación |

---

## 9. Resumen de Mejoras v3

| # | Mejora | Archivos modificados |
|---|--------|---------------------|
| 1 | Scraper paralelo con `asyncio.gather()` y timeout de 10s por query | `scraper.py` |
| 2 | FastAPI con `run_in_executor()` para no bloquear el event loop | `main.py` |
| 2 | Endpoint `/analyze/stream` con SSE para streaming de tokens | `main.py` |
| 2 | Endpoint `/health` con estado de Ollama y estadísticas de caché | `main.py` |
| 3 | Función `get_cache_hit_rate()` para monitoreo | `database.py` |
| 4 | Strategy Pattern: `BaseScraper` / `DuckDuckGoScraper` / `AccountIntelligenceEngine` | `agent.py` |
| 4 | Singleton Pattern: `OllamaClient` — LLM se instancia una sola vez | `agent.py`, `agents.py` |
| 4 | Dataclass `AnalysisResult` con propiedades `is_high_priority` y `summary` | `agent.py` |
| 5 | Patrones de prompt injection ampliados (10 patrones vs 4 en v2) | `schemas.py` |
| 5 | Protección SSRF en `company_url` (bloquea IPs privadas y localhost) | `schemas.py` |
| 5 | Campo `analysis_depth` con tres niveles: `quick / standard / deep` | `schemas.py` |
| 5 | Campo `report_language` cambiado a `Literal['en', 'es']` (tipo estricto) | `schemas.py` |
| 6 | Tracker de pipeline en vivo con 5 pasos animados (pending → active → done) | `App.jsx` |
| 7 | Score breakdown: 4 barras animadas por factor de puntuación | `App.jsx` |
| 8a | Botones "Re-analyze" y "Copy Speech" en cada fila del historial | `App.jsx` |
| 8b | Atajo de teclado `Ctrl+Enter` para ejecutar el análisis | `App.jsx` |
| 8c | Indicador de frescura de datos: verde < 1h, amarillo < 24h, rojo > 24h | `App.jsx` |
