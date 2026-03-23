# ============================================================
# KORHEX.AI — Script de arranque rápido
# Doble clic para levantar Ollama + Backend (FastAPI) + Frontend (React)
# ============================================================

$rootPath = $PSScriptRoot

# ── 0. Ollama (LLM local — llama3) ────────────────────────────
# Verificar si Ollama ya está corriendo
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $ollamaRunning = $true
        Write-Host "  Ollama ya está corriendo ✓" -ForegroundColor Green
    }
} catch {
    $ollamaRunning = $false
}

if (-not $ollamaRunning) {
    # Verificar si ollama está instalado
    $ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaPath) {
        Write-Host "  Iniciando Ollama..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList @(
            "-ExecutionPolicy", "Bypass",
            "-NoExit",
            "-Command",
            "ollama serve"
        ) -WindowStyle Minimized

        # Esperar a que Ollama esté listo
        Write-Host "  Esperando a que Ollama inicie..." -ForegroundColor Yellow
        $maxWait = 15
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 2
            $waited += 2
            try {
                $check = Invoke-WebRequest -Uri "http://localhost:11434/api/version" -TimeoutSec 2 -ErrorAction Stop
                if ($check.StatusCode -eq 200) {
                    Write-Host "  Ollama listo ✓" -ForegroundColor Green
                    break
                }
            } catch {
                Write-Host "  Esperando Ollama... ($waited/$maxWait s)" -ForegroundColor DarkGray
            }
        }

        # Verificar que el modelo llama3 está disponible
        try {
            $models = ollama list 2>&1
            if ($models -notmatch "llama3") {
                Write-Host "  Descargando modelo llama3 (esto puede tomar unos minutos)..." -ForegroundColor Yellow
                ollama pull llama3
            } else {
                Write-Host "  Modelo llama3 disponible ✓" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠ No se pudo verificar el modelo llama3" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "  ⚠ OLLAMA NO ESTÁ INSTALADO" -ForegroundColor Red
        Write-Host "  Descárgalo en: https://ollama.com/download" -ForegroundColor Yellow
        Write-Host "  Luego ejecuta: ollama pull llama3" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Presiona Enter para continuar sin Ollama (el análisis AI fallará)..." -ForegroundColor DarkGray
        Read-Host
    }
}

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
    "cd '$rootPath\frontend'; npm run dev"
) -WindowStyle Normal

# ── 3. Abrir el navegador automáticamente ───────────────────
Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "  KORHEX.AI arrancando..." -ForegroundColor Green
Write-Host "  Ollama   → http://localhost:11434" -ForegroundColor Cyan
Write-Host "  Backend  → http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend → http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
