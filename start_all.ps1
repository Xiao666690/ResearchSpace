# Start/restart the full ResearchSpace backend, Worker and frontend.
$ErrorActionPreference = 'Stop'
$backendDir = Join-Path $PSScriptRoot 'PaperQuery_Backend'
$pythonExe = Join-Path $backendDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Backend .venv is missing. See BACKEND_SETUP.md.' }
Push-Location $backendDir
try {
    & $pythonExe -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    & $pythonExe -m scripts.prepare_local_models
    if ($LASTEXITCODE -ne 0) { throw 'Embedding model preparation failed.' }
    & $pythonExe -m scripts.manage_local restart
    if ($LASTEXITCODE -ne 0) { throw 'Service startup failed. Check backend logs.' }
} finally { Pop-Location }
