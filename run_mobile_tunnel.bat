@echo off
setlocal
title AI Inventory Manager - Mobile HTTPS Tunnel (Cloudflare)
cd /d "%~dp0"

echo =========================================================================
echo         AI INVENTORY MANAGER - MOBILE CAMERA HTTPS TUNNEL
echo =========================================================================
echo.
echo  WHY THIS IS NEEDED:
echo  Mobile browsers (Chrome / Safari) strictly block camera access on
echo  plain HTTP (http://192.168.x.x:5000) for security.
echo  This tool creates a secure, trusted HTTPS link so your mobile camera
echo  works immediately without changing any phone settings.
echo.
echo  [1/2] Checking local Flask server...
netstat -ano | findstr :5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Note: Flask does not seem to be running on port 5000 yet.
    echo      Make sure run_windows.bat or run.bat is also running!
    echo.
) else (
    echo  [OK] Flask server detected on port 5000.
    echo.
)

echo  [2/2] Starting Cloudflare secure tunnel...
echo.
echo  -------------------------------------------------------------------------
echo   INSTRUCTIONS FOR MOBILE TESTING:
echo.
echo   1. Look below for the link ending in: .trycloudflare.com
echo      (Example: https://sample-words-here.trycloudflare.com)
echo.
echo   2. Open that HTTPS link on your phone (Chrome, Safari, etc.)
echo.
echo   3. When prompted, tap "Allow" for camera access.
echo      Your camera will now open and scan barcodes smoothly!
echo  -------------------------------------------------------------------------
echo.

cloudflared.exe tunnel --url http://127.0.0.1:5000

echo.
echo [INFO] Tunnel stopped.
pause
