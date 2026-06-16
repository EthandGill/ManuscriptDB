@echo off
REM ============================================================================
REM  start_localhost.bat — run ManuscriptDB locally and open it in the browser.
REM  Double-click this file. A window opens running the server; your browser
REM  opens to http://localhost:5000 a few seconds later.
REM  To stop the server: press Ctrl+C in this window (or just close it).
REM ============================================================================
cd /d "%~dp0"
title ManuscriptDB - Local Server (close to stop)

REM Open the browser a few seconds after the server starts (runs in parallel).
start "" cmd /c "timeout /t 4 >nul & start http://localhost:5000"

echo Starting the local server...  (browser will open at http://localhost:5000)
echo Leave this window open while you use the site. Ctrl+C to stop.
echo.
py app.py

echo.
echo (Server stopped.)
pause
