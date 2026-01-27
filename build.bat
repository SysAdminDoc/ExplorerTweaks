@echo off
REM ============================================================================
REM ExplorerTweaks Build Script
REM Compiles the application into a single portable executable
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   ExplorerTweaks Build Script v1.0
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [INFO] Python version: %PYVER%
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available.
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install -r requirements.txt --quiet
pip install pillow --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo       Done.

echo [2/5] Generating application icon...
if not exist "icon.ico" (
    python create_icon.py
    if errorlevel 1 (
        echo [WARNING] Could not generate icon. Using default.
    ) else (
        echo       Icon created successfully.
    )
) else (
    echo       Icon already exists, skipping.
)

echo [3/5] Cleaning previous builds...
if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul
echo       Done.

echo [4/5] Building executable...
echo       This may take a few minutes...
echo.

REM Build with version info if icon exists
if exist "icon.ico" (
    pyinstaller --noconfirm ^
        --onefile ^
        --windowed ^
        --name "ExplorerTweaks" ^
        --icon "icon.ico" ^
        --add-data "icon.ico;." ^
        --hidden-import "customtkinter" ^
        --collect-all "customtkinter" ^
        --version-file "version_info.txt" ^
        explorer_tweaks.py
) else (
    pyinstaller --noconfirm ^
        --onefile ^
        --windowed ^
        --name "ExplorerTweaks" ^
        --hidden-import "customtkinter" ^
        --collect-all "customtkinter" ^
        --version-file "version_info.txt" ^
        explorer_tweaks.py
)

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Common issues:
    echo   - Antivirus blocking PyInstaller
    echo   - Missing dependencies
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)

echo [5/5] Cleaning up build artifacts...
if exist "build" rmdir /s /q build 2>nul
if exist "ExplorerTweaks.spec" del /q ExplorerTweaks.spec 2>nul
echo       Done.

REM Get file size
for %%A in (dist\ExplorerTweaks.exe) do set SIZE=%%~zA
set /a SIZE_MB=%SIZE%/1048576

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo   Output:  dist\ExplorerTweaks.exe
echo   Size:    ~%SIZE_MB% MB
echo.
echo   The executable is portable and can be
echo   distributed as a single file.
echo.
echo ============================================
echo.

REM Ask if user wants to run the application
set /p RUNNOW="Run ExplorerTweaks now? (Y/N): "
if /i "%RUNNOW%"=="Y" (
    start "" "dist\ExplorerTweaks.exe"
)

pause
