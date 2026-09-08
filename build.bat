@echo off
setlocal
pushd "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File tools\Build-Release.ps1 %*
set BUILD_EXIT=%ERRORLEVEL%
popd
exit /b %BUILD_EXIT%
