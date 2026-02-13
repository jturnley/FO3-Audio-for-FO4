@echo off
REM FO3 Audio Builder - Quick CLI Build Script
REM Edit the paths below to match your installation

setlocal

REM === CONFIGURATION - EDIT THESE PATHS ===
set "FO3_DATA=C:\Program Files (x86)\Steam\steamapps\common\Fallout 3 goty\Data"
set "OUTPUT_DIR=output"
set "ARCHIVE2=C:\Program Files (x86)\Steam\steamapps\common\Fallout 4\Tools\Archive2\Archive2.exe"

REM === OPTIONAL: Enable verbose output ===
set "VERBOSE="
REM Uncomment the line below for detailed logging:
REM set "VERBOSE=--verbose"

echo ========================================
echo FO3 Audio Builder - CLI Mode
echo ========================================
echo.
echo Configuration:
echo   FO3 Data: %FO3_DATA%
echo   Output:   %OUTPUT_DIR%
echo   Archive2: %ARCHIVE2%
echo.

REM Check if FO3 Data folder exists
if not exist "%FO3_DATA%" (
    echo ERROR: Fallout 3 Data folder not found!
    echo Please edit build.bat and set the correct FO3_DATA path.
    echo.
    pause
    exit /b 1
)

REM Build command
echo Starting build...
echo.

python build_cli.py --fo3-data "%FO3_DATA%" --output-dir "%OUTPUT_DIR%" --archive2 "%ARCHIVE2%" %VERBOSE%

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo BUILD COMPLETE!
    echo ========================================
    echo.
    echo Output location: %OUTPUT_DIR%\final\Fallout3Audio\
    echo.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo Error code: %ERRORLEVEL%
    echo.
)

pause
