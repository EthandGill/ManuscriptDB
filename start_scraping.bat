@echo off
REM ============================================================================
REM  start_scraping.bat  —  one-click papyri scraper (no VS Code needed)
REM  Double-click this file. It scrapes the ranges in sweep_ranges.txt into
REM  _sweep_*.json using your Firecrawl credits. Close the window to stop.
REM ============================================================================
setlocal
cd /d "%~dp0"
title ManuscriptDB - Papyri Scraper

where python >nul 2>nul
if errorlevel 1 (
  echo [error] Python is not installed / not on PATH. Install Python first.
  echo         https://www.python.org/downloads/  (tick "Add python.exe to PATH")
  pause & exit /b 1
)

REM --- Firecrawl key: use the env var, or read a local .firecrawl_key file ---
if not defined FIRECRAWL_API_KEY (
  if exist "%~dp0.firecrawl_key" set /p FIRECRAWL_API_KEY=<"%~dp0.firecrawl_key"
)
if not defined FIRECRAWL_API_KEY (
  echo.
  echo [!] FIRECRAWL_API_KEY is not set, so scraping cannot start.
  echo     Set it once in PowerShell - see SCRAPING-credit-strategy.md for the
  echo     exact command - then double-click this file again.
  echo.
  pause & exit /b 1
)

echo Preparing scraper libraries (first run only, then it's instant)...
python -m pip install --quiet firecrawl-py truststore 2>nul

echo.
echo ============================================================================
echo  Scraping papyri from the ranges in sweep_ranges.txt
echo  Output: _sweep_*.json in this folder. ~1 Firecrawl credit per id.
echo  You can close this window any time to stop; re-running resumes.
echo ============================================================================
echo.
python parallel_sweep.py 4

echo.
echo ===== Done. Banked _sweep_*.json. Translate them in Claude Code next. =====
pause
endlocal
