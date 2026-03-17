# KORHEX.AI Enterprise 🛡️🤖

![KORHEX.AI](korhex-logo.png)

**KORHEX.AI** es una plataforma de **Enterprise Account Intelligence** diseñada estrictamente en torno a una arquitectura **"Zero Data Leakage"** (Cero Fuga de Datos). Realiza análisis profundos de cuentas B2B operando completamente de forma local, asegurando que la información sensible y estratégica nunca salga del entorno corporativo.

## 🏗️ Arquitectura Técnica (v2.0)

El sistema ha sido refactorizado por completo, pasando de una prueba de concepto monolítica a una arquitectura desacoplada, escalable y de grado empresarial:

### 1. Frontend (React 18 + Vite + Tailwind CSS)
- **UI/UX:** Un panel moderno con tema oscuro, diseñado a medida para Account Managers, que presenta 5 pestañas distintas de inteligencia (`Overview`, `Intelligence`, `Sales Speech`, `Products`, `Privacy Audit`).
- **Gestión de Estado:** Seguimiento del historial local completamente funcional y preferencias de usuario (Nombre, Industria predeterminada, Idioma del reporte).
- **Red:** Peticiones de datos asíncronas equipadas con `AbortController` para cancelar ejecuciones de agentes en vuelo de manera elegante.

### 2. Backend (FastAPI + Pydantic)
- **Framework Principal:** API REST asíncrona de alto rendimiento impulsada por FastAPI.
- **Validación de Datos:** Mecanismos estrictos de validación de entrada/salida y prevención de Inyección de Prompts utilizando **Pydantic V2**.
- **Esqueleto de Autenticación:** Preparado para integración empresarial con JWT.

### 3. Orquestación de IA (CrewAI + Llama 3)
- **Sistema Multi-Agente:** Emplea `CrewAI` para ejecutar agentes de razonamiento secuencial (Analista de Inteligencia, Especialista Senior de Ventas).
- **Ejecución Zero Data Leakage:** Utiliza **Llama 3** ejecutándose localmente a través de **Ollama**. *No se utilizan APIs de IA externas (OpenAI, Anthropic).*
- **Web Scraping Corporativo:** Se reemplazaron los scrapers de APIs públicas (Tavily) por `duckduckgo-search` enrutado estrictamente a través de un proxy corporativo interno (`CORP_PROXY_URL`) para asegurar un completo anonimato en las búsquedas.

---

## 💾 Estructuras de Datos y Esquemas

La aplicación impone un contrato de datos estricto entre el frontend y el backend utilizando Pydantic:

### `AnalysisRequest`
Valida las entradas para evitar inyecciones de prompts y manejar configuraciones predeterminadas:
- `company_name`: `str` (Validado con Regex contra inyecciones)
- `company_url`: `HttpUrl`
- `industry`: `str`
- `years_inactive`: `int` (Rango: 0-20)
- `report_language`: `str` (`en` o `es` — Inyectado directamente en los prompts de sistema de Llama 3)

### `AnalysisResponse`
Un payload JSON unificado que consolida la salida del scraper, el emparejamiento de portafolio RAG y los agentes de CrewAI:
- `company_name` & `lead_score`
- `data_quality` & `data_warning`
- `intelligence_report` (Formateado con etiquetas de parseo `[SECTION_N]` para la UI)
- `sales_speech` (Limitado a 240 palabras por el Agente Auditor)
- `audit_passed` & `audit_notes`
- `products` (Matriz de mapeos de productos enfocados en ROI)
- `recent_news` & `sources`

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Node.js (v18+)
- Python (v3.12+)
- Ollama ejecutándose localmente con el modelo `llama3` descargado (`ollama run llama3`)

### Variables de Entorno (`backend/.env`)
```env
CORP_PROXY_URL=http://tu-proxy-corporativo:puerto
JWT_SECRET=tu_clave_secreta_super_segura_jwt
```

### Inicio Rápido con 1 Clic (Windows)
Ejecuta el script de PowerShell proporcionado desde el directorio raíz para iniciar automáticamente tanto el backend de FastAPI como el frontend de Vite:
```powershell
.\start.ps1
```

### Inicio Manual
**Backend:**
```bash
cd backend
.\venv_backend\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Políticas de Seguridad
- **Aislamiento Estricto de Red:** Todo el razonamiento del LLM ocurre en `127.0.0.1:11434`.
- **Higiene de Git:** Las dependencias (`node_modules`, `venv_backend`), las variables de entorno (`.env`) y los artefactos del sistema operativo están correctamente ignorados en `.gitignore`.
