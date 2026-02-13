# FO3 Audio Builder - PowerShell Build Script
# Edit the paths below to match your installation

# === CONFIGURATION - EDIT THESE PATHS ===
$fo3Data = "C:\Program Files (x86)\Steam\steamapps\common\Fallout 3 goty\Data"
$outputDir = "output"
$archive2 = "C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Tools\Archive2\Archive2.exe"

# === OPTIONAL: Enable verbose output ===
$verbose = $false  # Set to $true for detailed logging

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FO3 Audio Builder - CLI Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:"
Write-Host "  FO3 Data: $fo3Data"
Write-Host "  Output:   $outputDir"
Write-Host "  Archive2: $archive2"
Write-Host ""

# Check if FO3 Data folder exists
if (-not (Test-Path $fo3Data)) {
    Write-Host "ERROR: Fallout 3 Data folder not found!" -ForegroundColor Red
    Write-Host "Please edit build.ps1 and set the correct `$fo3Data path." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Build arguments
$args = @(
    "build_cli.py",
    "--fo3-data", $fo3Data,
    "--output-dir", $outputDir,
    "--archive2", $archive2
)

if ($verbose) {
    $args += "--verbose"
}

# Run build
Write-Host "Starting build..." -ForegroundColor Green
Write-Host ""

$process = Start-Process -FilePath "python" -ArgumentList $args -Wait -NoNewWindow -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output location: $outputDir\final\Fallout3Audio\" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error code: $($process.ExitCode)" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
