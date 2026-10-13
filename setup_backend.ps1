param([string]$PythonPath)
$ErrorActionPreference = 'Stop'
$backendDir=Join-Path $PSScriptRoot 'PaperQuery_Backend'
$pythonExe=Join-Path $backendDir '.venv\Scripts\python.exe'
Push-Location $backendDir
try {
    if (-not (Test-Path -LiteralPath $pythonExe)) {
        if (-not $PythonPath) {
            $bundledPython=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
            if (Test-Path -LiteralPath $bundledPython) { $PythonPath=$bundledPython }
            else { throw 'Supply a Python 3.12 executable: .\setup_backend.ps1 -PythonPath C:\path\python.exe' }
        }
        & $PythonPath -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
    }
    & $pythonExe -m pip install -r requirements-win-full.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    if (-not (Test-Path -LiteralPath '.env')) {
        $configText=Get-Content -LiteralPath '.env.example' -Raw
        $secret=[guid]::NewGuid().ToString('N')+[guid]::NewGuid().ToString('N')
        $configText=$configText.Replace('SECRET_KEY=change-me','SECRET_KEY='+$secret)
        Set-Content -LiteralPath '.env' -Value $configText -Encoding utf8
    }
    & $pythonExe -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    & $pythonExe -m scripts.prepare_local_models
    if ($LASTEXITCODE -ne 0) { throw 'Model preparation failed.' }
    & $pythonExe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency check failed.' }
    Write-Host 'Setup complete. Enter your key with configure_api.ps1, then run start_all.ps1.'
} finally { Pop-Location }
