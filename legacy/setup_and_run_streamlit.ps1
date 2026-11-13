# Run from your own PowerShell; first setup needs internet access.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
    }
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    & $projectPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check internet access and the error above.' }
    & $projectPython init_db.py
    if ($LASTEXITCODE -ne 0) { throw 'Database/model setup failed. Check the error above before continuing.' }
    & $projectPython tests/smoke_check.py
    if ($LASTEXITCODE -ne 0) { throw 'Full smoke tests failed. The app has not been verified.' }
    & $projectPython tests/ui_check.py
    if ($LASTEXITCODE -ne 0) { throw 'UI checks failed. Check the error above.' }
    Write-Host 'Setup and tests passed. Opening Streamlit at http://localhost:8501'
    & $projectPython -m streamlit run app.py
    if ($LASTEXITCODE -ne 0) { throw 'Streamlit exited with an error.' }
} finally {
    Pop-Location
}
