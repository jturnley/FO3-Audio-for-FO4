# Build Executable - Quick Build Script
# This script creates a standalone Windows executable for distribution

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "FO3 AUDIO BUILDER - EXECUTABLE BUILD" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "[1/5] Checking dependencies..." -ForegroundColor Yellow
try {
    $null = & python -c "import PyInstaller" 2>&1
    Write-Host "  ✓ PyInstaller found" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PyInstaller not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    & python -m pip install pyinstaller
}

try {
    $null = & python -c "import PyQt6" 2>&1
    Write-Host "  ✓ PyQt6 found" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PyQt6 not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    & python -m pip install -r requirements.txt
}

Write-Host ""

# Clean previous builds
Write-Host "[2/5] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
    Write-Host "  ✓ Cleaned dist/" -ForegroundColor Green
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
    Write-Host "  ✓ Cleaned build/" -ForegroundColor Green
}
Write-Host ""

# Build executable using spec file
Write-Host "[3/5] Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "  This may take 2-5 minutes..." -ForegroundColor Gray
Write-Host ""

$buildStart = Get-Date
& python -m PyInstaller FO3AudioBuilder.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

$buildTime = ((Get-Date) - $buildStart).TotalSeconds
Write-Host ""
Write-Host "  ✓ Build completed in $([math]::Round($buildTime, 1)) seconds" -ForegroundColor Green
Write-Host ""

# Verify output
Write-Host "[4/5] Verifying build..." -ForegroundColor Yellow
$exePath = "dist\FO3AudioBuilder.exe"

if (Test-Path $exePath) {
    $exeSize = [math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Host "  ✓ Executable created: $exePath" -ForegroundColor Green
    Write-Host "  ✓ Size: $exeSize MB" -ForegroundColor Green
} else {
    Write-Host "  ✗ Executable not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create distribution package
Write-Host "[5/5] Creating distribution package..." -ForegroundColor Yellow

$version = "1.3.0"  # Update this with each release
$distFolder = "dist\FO3AudioBuilder_v$version"

# Create distribution folder
if (Test-Path $distFolder) {
    Remove-Item $distFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $distFolder -Force | Out-Null

# Copy executable
Copy-Item $exePath $distFolder

# Copy documentation
Copy-Item "README.md" $distFolder
Copy-Item "LICENSE" $distFolder
Copy-Item "CHANGELOG.md" $distFolder
Copy-Item "CLI_GUIDE.md" $distFolder
Copy-Item "QUICK_REFERENCE.md" $distFolder

# Create quick start guide
$quickStart = @"
# FO3 Audio Builder - Quick Start

## For End Users (GUI Mode)

1. Double-click `FO3AudioBuilder.exe` to launch the GUI
2. Browse to your Fallout 3 Data folder
3. Browse to your output folder (where to save the BA2)
4. Click "Build"

## Command Line Mode

Open PowerShell or Command Prompt in this folder:

``````
FO3AudioBuilder.exe --fo3-data "C:\Games\Fallout 3\Data"
``````

## Requirements

- Fallout 3 GOTY Edition (for source audio files)
- Archive2.exe (from FO4 Creation Kit) - recommended for best compatibility

## Documentation

- README.md - Full documentation
- CLI_GUIDE.md - Command-line usage guide
- QUICK_REFERENCE.md - Quick command reference
- CHANGELOG.md - Version history

## Troubleshooting

If the application won't start:
- Make sure you have Windows 10 or later
- Run as Administrator if needed
- Check antivirus isn't blocking it

For more help, see README.md
"@

Set-Content -Path "$distFolder\QUICK_START.txt" -Value $quickStart

Write-Host "  ✓ Created distribution folder: $distFolder" -ForegroundColor Green
Write-Host ""

# Create ZIP archive
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "dist\FO3AudioBuilder_v${version}.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $distFolder -DestinationPath $zipPath -CompressionLevel Optimal
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "  ✓ Created: $zipPath ($zipSize MB)" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Executable:" -ForegroundColor Cyan
Write-Host "  Location: $exePath"
Write-Host "  Size: $exeSize MB"
Write-Host ""
Write-Host "Distribution Package:" -ForegroundColor Cyan
Write-Host "  Folder: $distFolder"
Write-Host "  ZIP: $zipPath ($zipSize MB)"
Write-Host ""
Write-Host "Testing:" -ForegroundColor Cyan
Write-Host "  Run: .\$exePath --help"
Write-Host "  GUI: .\$exePath"
Write-Host ""
Write-Host "Ready for distribution!" -ForegroundColor Green
Write-Host ""
