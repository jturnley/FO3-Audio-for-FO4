@echo off
REM Build Executable - Windows Batch Script
REM This script creates a standalone Windows executable for distribution

echo ======================================================================
echo FO3 AUDIO BUILDER - EXECUTABLE BUILD
echo ======================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)

REM Check PyInstaller
echo [1/5] Checking dependencies...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo   Installing PyInstaller...
    python -m pip install pyinstaller
)

python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo   Installing required packages...
    python -m pip install -r requirements.txt
)

echo   OK - Dependencies ready
echo.

REM Clean previous builds
echo [2/5] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo   OK - Cleaned build directories
echo.

REM Build executable
echo [3/5] Building executable with PyInstaller...
echo   This may take 2-5 minutes...
echo.

python -m PyInstaller FO3AudioBuilder.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo   OK - Build completed
echo.

REM Verify output
echo [4/5] Verifying build...
if not exist "dist\FO3AudioBuilder.exe" (
    echo   ERROR: Executable not found!
    pause
    exit /b 1
)

echo   OK - Executable created
echo.

REM Create distribution package
echo [5/5] Creating distribution package...

set VERSION=1.3.0
set DIST_FOLDER=dist\FO3AudioBuilder_v%VERSION%

if exist "%DIST_FOLDER%" rmdir /s /q "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%"

copy "dist\FO3AudioBuilder.exe" "%DIST_FOLDER%\"
copy "README.md" "%DIST_FOLDER%\"
copy "LICENSE" "%DIST_FOLDER%\"
copy "CHANGELOG.md" "%DIST_FOLDER%\"
copy "CLI_GUIDE.md" "%DIST_FOLDER%\"
copy "QUICK_REFERENCE.md" "%DIST_FOLDER%\"

echo   OK - Distribution folder created
echo.

REM Summary
echo ======================================================================
echo BUILD COMPLETE!
echo ======================================================================
echo.
echo Executable: dist\FO3AudioBuilder.exe
echo Distribution: %DIST_FOLDER%
echo.
echo To test:
echo   dist\FO3AudioBuilder.exe --help
echo.
echo Ready for distribution!
echo.

pause
