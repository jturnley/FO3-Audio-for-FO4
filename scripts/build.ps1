# Build FO3 Audio Builder Executable
# Uses the project venv to build with PyInstaller

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== FO3 Audio Builder - Build ===" -ForegroundColor Cyan

# Check venv exists
$VenvPath = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERROR: Virtual environment not found. Run setup_venv.ps1 first." -ForegroundColor Red
    exit 1
}

$PyInstaller = Join-Path $VenvPath "Scripts\pyinstaller.exe"
$Python = Join-Path $VenvPath "Scripts\python.exe"

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
$DistPath = Join-Path $ProjectRoot "dist"
$BuildPath = Join-Path $ProjectRoot "build"
if (Test-Path $DistPath) { Remove-Item $DistPath -Recurse -Force }
if (Test-Path $BuildPath) { Remove-Item $BuildPath -Recurse -Force }

# Build
Write-Host "Building executable..." -ForegroundColor Yellow
Push-Location $ProjectRoot
& $PyInstaller --onefile --windowed `
    --name "FO3AudioBuilder" `
    --hidden-import=PyQt6 `
    --hidden-import=PyQt6.QtWidgets `
    --hidden-import=PyQt6.QtCore `
    --hidden-import=PyQt6.QtGui `
    src/main.py `
    --noconfirm
Pop-Location

# Check result
$ExePath = Join-Path $DistPath "FO3AudioBuilder.exe"
if (Test-Path $ExePath) {
    $Size = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output: $ExePath"
    Write-Host "Size: $Size MB"
} else {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}
