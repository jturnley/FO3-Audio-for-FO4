# Run FO3 Audio Builder GUI (from source)
# Uses the project venv

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$VenvPath = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERROR: Virtual environment not found. Run setup_venv.ps1 first." -ForegroundColor Red
    exit 1
}

$Python = Join-Path $VenvPath "Scripts\python.exe"
& $Python (Join-Path $ProjectRoot "src\main.py") --gui
