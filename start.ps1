# ============================================================
# KORHEX.AI — Script de arranque rápido
# Doble clic para levantar Backend (FastAPI) + Frontend (React)
# ============================================================

$rootPath = $PSScriptRoot

# ── 1. Backend (FastAPI en puerto 8000) ──────────────────────
Start-Process powershell -ArgumentList @(
    "-ExecutionPolicy", "Bypass",
    "-NoExit",
    "-Command",
    "cd '$rootPath\backend'; .\venv_backend\Scripts\activate; uvicorn main:app --reload --port 8000"
) -WindowStyle Normal

# ── 2. Frontend (React/Vite en puerto 5173) ─────────────────
Start-Process powershell -ArgumentList @(
    "-ExecutionPolicy", "Bypass",
    "-NoExit",
    "-Command",
    "cd '$rootPath\\frontend'; npm run dev"
) -WindowStyle Normal

# ── 3. Abrir el navegador automáticamente ───────────────────
Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "  KORHEX.AI arrancando..." -ForegroundColor Green
Write-Host "  Backend  → http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend → http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
