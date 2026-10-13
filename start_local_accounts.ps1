$ErrorActionPreference = 'Stop'
$backendDir = Join-Path $PSScriptRoot 'PaperQuery_Backend'
$frontendDir = Join-Path $PSScriptRoot 'PaperQuery_Frontend'
$pythonExe = Join-Path $backendDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Backend .venv is missing.' }
Push-Location $backendDir
try {
    & $pythonExe -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
} finally { Pop-Location }
$backendRunning = $false
try {
    $response = Invoke-RestMethod 'http://127.0.0.1:8001/local/status' -TimeoutSec 3
    if ($response.service -ne 'researchspace-local') { throw 'Unexpected service on port 8001.' }
    $backendRunning = $true
} catch {
    if (Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue) {
        throw 'Port 8001 is occupied. Check the existing service before starting local mode.'
    }
}
if (-not $backendRunning) {
    Start-Process -FilePath $pythonExe -ArgumentList '-m','uvicorn','local_main:app','--host','127.0.0.1','--port','8001' -WorkingDirectory $backendDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $backendDir 'local-api.log') -RedirectStandardError (Join-Path $backendDir 'local-api-error.log')
}
$frontendRunning = $false
try {
    $frontendPage = Invoke-WebRequest 'http://127.0.0.1:8080/login' -UseBasicParsing -TimeoutSec 10
    $frontendRunning = $frontendPage.Content.Contains('/@vite/client')
} catch {}
if (-not $frontendRunning) {
    if (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 8080 is occupied by a different service.' }
    $nodeExe = (Get-Command node.exe -ErrorAction Stop).Source
    Start-Process -FilePath $nodeExe -ArgumentList 'node_modules/vite/bin/vite.js','--mode','dev','--host','127.0.0.1','--port','8080','--strictPort' -WorkingDirectory $frontendDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $frontendDir 'vite-local.log') -RedirectStandardError (Join-Path $frontendDir 'vite-local-error.log')
}
Write-Host 'Local accounts/workspace mode: http://127.0.0.1:8080/login'
Write-Host 'AI features require full backend setup. See LOCAL_PROJECT_GUIDE.md.'
