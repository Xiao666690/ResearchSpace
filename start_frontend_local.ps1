$ErrorActionPreference = 'Stop'
$frontendDir = Join-Path $PSScriptRoot 'PaperQuery_Frontend'
if (-not (Test-Path -LiteralPath (Join-Path $frontendDir 'node_modules\vite\bin\vite.js'))) {
    throw 'Frontend dependencies are missing. Run npm ci with HUSKY=0 in PaperQuery_Frontend first.'
}
$listener = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host 'Port 8080 is already in use. Existing frontend: http://127.0.0.1:8080/login'
    exit 0
}
Push-Location $frontendDir
try {
    & node 'node_modules/vite/bin/vite.js' --mode dev --host 127.0.0.1 --port 8080 --strictPort
} finally {
    Pop-Location
}
