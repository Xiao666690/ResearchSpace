$ErrorActionPreference = 'Stop'
$backendDir=Join-Path $PSScriptRoot 'PaperQuery_Backend'
Push-Location $backendDir
try { & '.\.venv\Scripts\python.exe' -m scripts.manage_local stop }
finally { Pop-Location }
