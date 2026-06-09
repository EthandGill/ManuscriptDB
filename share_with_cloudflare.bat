@echo off
REM ============================================================================
REM  share_with_cloudflare.bat  —  put ManuscriptDB on a public link (FREE)
REM ----------------------------------------------------------------------------
REM  Self-contained: downloads cloudflared.exe straight into this folder if it
REM  isn't already here (no winget, no install, no admin needed), starts the
REM  Flask app, and opens a free Cloudflare quick tunnel.
REM
REM  You get a public URL like   https://random-words-1234.trycloudflare.com
REM  that anyone can open while this window stays running.
REM
REM  HOW TO USE:  just double-click this file.
REM  TO STOP:     press Ctrl+C in this window (and close the server window).
REM
REM  NOTE: the URL is temporary and changes every time you run this.
REM ============================================================================

cd /d "%~dp0"

REM --- 1. Locate cloudflared ----------------------------------------------
REM Prefer a copy sitting next to this script; fall back to one on PATH.
set "CF=%~dp0cloudflared.exe"

if exist "%CF%" goto have_cf

where cloudflared >nul 2>nul
if not errorlevel 1 (
    set "CF=cloudflared"
    goto have_cf
)

echo [setup] cloudflared not found. Downloading it into this folder...
echo         (about 18 MB from the official Cloudflare GitHub release)
powershell -NoProfile -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF%' } catch { Write-Host $_.Exception.Message; exit 1 }"

if not exist "%CF%" (
    echo.
    echo [error] Download failed. Check your internet connection, or download
    echo         cloudflared-windows-amd64.exe manually from
    echo           https://github.com/cloudflare/cloudflared/releases/latest
    echo         rename it to  cloudflared.exe  and drop it in this folder,
    echo         then run this script again.
    echo.
    pause
    exit /b 1
)
echo [setup] cloudflared downloaded.

:have_cf

REM --- 2. Make sure Python is available -----------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [error] Python is not on your PATH, so 'python app.py' can't start.
    echo         Install Python from https://www.python.org/downloads/ and
    echo         tick "Add python.exe to PATH" during setup, then re-run this.
    echo.
    pause
    exit /b 1
)

REM --- 3. Start the Flask server in its own window -------------------------
echo [run] Starting ManuscriptDB (python app.py) in a separate window...
start "ManuscriptDB server" cmd /k "cd /d "%~dp0" && python app.py"

echo [run] Waiting a few seconds for the server to come up...
timeout /t 5 /nobreak >nul

REM --- 4. Open the public tunnel ------------------------------------------
echo.
echo ============================================================================
echo  Opening a public Cloudflare link to http://localhost:5000
echo  Look for the   https://....trycloudflare.com   URL printed below.
echo  Share THAT link. Keep this window open while people use the site.
echo  Press Ctrl+C here to stop sharing.
echo ============================================================================
echo.
"%CF%" tunnel --url http://localhost:5000

echo.
echo (Tunnel closed.) Press any key to exit.
pause >nul
