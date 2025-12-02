# Setup/Update Virtual Environment for FO3 Audio Builder
# Run this script to create or update the venv

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== FO3 Audio Builder - Setup/Update venv ===" -ForegroundColor Cyan

# Check if venv exists
$VenvPath = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
}

# Activate and upgrade pip
Write-Host "Activating venv and upgrading pip..." -ForegroundColor Yellow
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip --quiet

# Install/update requirements
Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
& "$VenvPath\Scripts\pip.exe" install -r (Join-Path $ProjectRoot "requirements.txt") --upgrade

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "To activate manually: .\.venv\Scripts\Activate.ps1"
Write-Host "To build exe: .\scripts\build.ps1"
