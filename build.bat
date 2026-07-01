@echo off
REM ============================================================================
REM ExplorerTweaks Build Script
REM Compiles the application into a single portable executable
REM ============================================================================

setlocal enabledelayedexpansion

set APP_VERSION=2.15.0
set RELEASE_BASENAME=ExplorerTweaks-v%APP_VERSION%-win64
set CHECKSUM_FILE=ExplorerTweaks-v%APP_VERSION%-SHA256SUMS.txt
set ZIP_FILE=%RELEASE_BASENAME%.zip
set GENERATED_ICON=0

echo.
echo ============================================
echo   ExplorerTweaks Build Script v%APP_VERSION%
echo ============================================
echo.

set PIP_DISABLE_PIP_VERSION_CHECK=1
set BUILD_VENV=.build-venv
set BUILD_PY=%BUILD_VENV%\Scripts\python.exe

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from python.org
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [INFO] Python version: %PYVER%
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available.
    exit /b 1
)

echo [1/7] Creating pinned build environment...
if exist "%BUILD_VENV%" rmdir /s /q "%BUILD_VENV%" 2>nul

python -m venv "%BUILD_VENV%"
if errorlevel 1 (
    echo [ERROR] Failed to create build virtual environment.
    exit /b 1
)

"%BUILD_PY%" -m pip install --requirement requirements.txt --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

"%BUILD_PY%" -m pip check
if errorlevel 1 (
    echo [ERROR] Dependency check failed.
    exit /b 1
)
echo       Done.

echo [2/7] Generating application icon...
if not exist "icon.ico" (
    "%BUILD_PY%" create_icon.py
    if errorlevel 1 (
        echo [WARNING] Could not generate icon. Using default.
    ) else (
        set GENERATED_ICON=1
        echo       Icon created successfully.
    )
) else (
    echo       Icon already exists, skipping.
)

echo [3/7] Cleaning previous builds...
if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul
echo       Done.

echo [4/7] Building executable...
echo       This may take a few minutes...
echo.

"%BUILD_PY%" -m PyInstaller --noconfirm ExplorerTweaks.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Common issues:
    echo   - Antivirus blocking PyInstaller
    echo   - Missing dependencies
    echo   - Insufficient disk space
    echo.
    exit /b 1
)

echo [5/7] Signing executable if a certificate is available...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$certs = @(Get-ChildItem Cert:\CurrentUser\My, Cert:\LocalMachine\My -ErrorAction SilentlyContinue | Where-Object { $_.HasPrivateKey -and ($_.EnhancedKeyUsageList | Where-Object { $_.FriendlyName -eq 'Code Signing' -or $_.ObjectId -eq '1.3.6.1.5.5.7.3.3' }) } | Sort-Object NotAfter -Descending); if ($certs.Count -eq 0) { Write-Host '[WARNING] No code-signing cert found; skipping signing.'; exit 0 }; $sig = Set-AuthenticodeSignature -FilePath 'dist\ExplorerTweaks.exe' -Certificate $certs[0] -TimestampServer 'http://timestamp.digicert.com'; if ($sig.Status -ne 'Valid') { Write-Host ('[ERROR] Signing failed: ' + $sig.Status); exit 1 }; Write-Host ('      Signed with ' + $certs[0].Subject)"
if errorlevel 1 (
    echo [ERROR] Signing failed.
    exit /b 1
)
echo       Done.

echo [6/7] Creating release package and checksums...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; function Get-Sha256Hex([string]$Path) { $resolved = (Resolve-Path -LiteralPath $Path).Path; $sha = [System.Security.Cryptography.SHA256]::Create(); $stream = [System.IO.File]::OpenRead($resolved); try { return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() } finally { $stream.Dispose(); $sha.Dispose() } }; $dist = 'dist'; $install = Join-Path $dist 'INSTALL.txt'; $checksum = Join-Path $dist $env:CHECKSUM_FILE; $zip = Join-Path $dist $env:ZIP_FILE; $notes = @(('ExplorerTweaks v' + $env:APP_VERSION), '', 'Install:', '1. Download ExplorerTweaks.exe or the versioned ZIP.', '2. If using the ZIP, extract it to a folder you control.', '3. Run ExplorerTweaks.exe. No installer or administrator rights are required for normal per-user settings.', '', 'Uninstall:', '1. Use the Tools page to remove Shell Menu and Auto Dark integrations if they were installed.', '2. Delete ExplorerTweaks.exe and any extracted release files.', '', 'Verify:', ('Run Get-FileHash -Algorithm SHA256 ExplorerTweaks.exe and compare it with ' + $env:CHECKSUM_FILE + '.')); Set-Content -LiteralPath $install -Value $notes -Encoding UTF8; $lines = @(); foreach ($name in @('ExplorerTweaks.exe', 'INSTALL.txt')) { $path = Join-Path $dist $name; $hash = Get-Sha256Hex $path; $lines += ($hash + '  ' + $name) }; Set-Content -LiteralPath $checksum -Value $lines -Encoding ASCII; if (Test-Path $zip) { Remove-Item -LiteralPath $zip -Force }; Compress-Archive -LiteralPath (Join-Path $dist 'ExplorerTweaks.exe'), $install, $checksum -DestinationPath $zip -Force; $zipHash = Get-Sha256Hex $zip; Add-Content -LiteralPath $checksum -Value ($zipHash + '  ' + $env:ZIP_FILE) -Encoding ASCII; Write-Host ('      ZIP: ' + $zip); Write-Host ('      Checksums: ' + $checksum)"
if errorlevel 1 (
    echo [ERROR] Release packaging failed.
    exit /b 1
)
echo       Done.

echo [7/7] Cleaning up build artifacts...
if exist "build" rmdir /s /q build 2>nul
if exist "%BUILD_VENV%" rmdir /s /q "%BUILD_VENV%" 2>nul
if "%GENERATED_ICON%"=="1" if exist "icon.ico" del /q "icon.ico" 2>nul
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
echo   ZIP:     dist\%ZIP_FILE%
echo   SHA256:  dist\%CHECKSUM_FILE%
echo   Notes:   dist\INSTALL.txt
echo   Size:    ~%SIZE_MB% MB
echo.
echo   The executable is portable and can be
echo   distributed as a single file.
echo.
echo ============================================
echo.

exit /b 0
