@echo off
title Goldsmith Ledger Launcher
echo.
echo ========================================
echo     🏆 Goldsmith Ledger Launcher
echo ========================================
echo.
echo Starting your goldsmith ledger...
echo.

REM Check if the HTML file exists
if not exist "goldsmith-ledger-offline.html" (
    echo ❌ Error: goldsmith-ledger-offline.html not found!
    echo Please ensure the HTML file is in the same folder as this launcher.
    echo.
    pause
    exit /b 1
)

REM Try to open with different browsers
echo 🔍 Looking for web browser...

REM Try Chrome first
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✅ Opening with Google Chrome...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="file:///%CD%\goldsmith-ledger-offline.html"
    goto :success
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✅ Opening with Google Chrome...
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --app="file:///%CD%\goldsmith-ledger-offline.html"
    goto :success
)

REM Try Edge
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo ✅ Opening with Microsoft Edge...
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="file:///%CD%\goldsmith-ledger-offline.html"
    goto :success
)

REM Try default browser
echo ✅ Opening with default browser...
start "" "goldsmith-ledger-offline.html"

:success
echo.
echo 🚀 Goldsmith Ledger is starting...
echo 💡 Tip: Bookmark this page for easy access next time!
echo.
echo Press any key to close this window...
pause >nul
exit