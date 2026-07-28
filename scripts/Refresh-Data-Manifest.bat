@echo off
echo Scanning Data folder and rebuilding the source-file manifest...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update-manifest.ps1"
echo.
pause
