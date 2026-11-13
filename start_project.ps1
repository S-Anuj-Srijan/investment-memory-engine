param([switch]$Build)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw 'Create .venv and install requirements.txt first; see README.md.' }
if (-not (Test-Path '.env')) { throw 'Configure .env first; see README.md.' }
if (-not (Test-Path 'web/node_modules/next/dist/bin/next')) {
    throw 'Install the web dependencies first: cd web; npm.cmd ci'
}
if (Test-Path 'data/postgres/PG_VERSION') {
    & $python scripts/local_postgres.py
    if ($LASTEXITCODE -ne 0) { throw 'Could not start local PostgreSQL.' }
}
& $python -m backend.manage init
if ($LASTEXITCODE -ne 0) { throw 'Database initialization failed.' }
if ($Build -or -not (Test-Path 'web/.next/BUILD_ID')) {
    Push-Location web
    try {
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Next.js build failed.' }
    } finally { Pop-Location }
}
$apiProcess = Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','backend.api:app','--host','127.0.0.1','--port','8000') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
try {
    Write-Host 'Open http://localhost:3000. Press Ctrl+C to stop the web application.'
    Push-Location web
    try { & node node_modules/next/dist/bin/next start --hostname 127.0.0.1 }
    finally { Pop-Location }
} finally {
    if (-not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id }
}
