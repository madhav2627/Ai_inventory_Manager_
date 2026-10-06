@echo off
setlocal
title AI Inventory Manager (HTTPS Mode for Mobile Camera)
cd /d "%~dp0"

echo =========================================================================
echo         AI INVENTORY MANAGER - LOCAL HTTPS MODE (SSL)
echo =========================================================================
echo.
echo  Starting server in HTTPS mode using cert.pem and key.pem...
echo  Your mobile browser will show a security warning ("Not private") on
echo  the first visit because the certificate is self-signed:
echo    - Tap "Advanced"
echo    - Tap "Proceed to 192.168.0.104 (unsafe)"
echo  Once accepted, camera permissions will work directly!
echo.

set VENV_DIR=%~dp0venv
if exist "%VENV_DIR%\Scripts\python.exe" (
    "%VENV_DIR%\Scripts\python.exe" "%~dp0app.py" --https
) else (
    python "%~dp0app.py" --https
)

pause
