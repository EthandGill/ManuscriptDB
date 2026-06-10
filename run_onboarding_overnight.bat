@echo off
REM ============================================================================
REM  run_onboarding_overnight.bat  —  unattended documentary onboarding run
REM ----------------------------------------------------------------------------
REM  Runs Claude Code headless to process a few ranges from onboarding_queue.txt
REM  per the queue-driven loop in WORKFLOW-manuscript-onboarding.md (section 8),
REM  with no prompts and a timestamped log. Built for Windows Task Scheduler.
REM
REM  Usage:
REM     run_onboarding_overnight.bat            (process 2 ranges, the default)
REM     run_onboarding_overnight.bat 4          (process up to 4 ranges)
REM
REM  Schedule it (run from an *Administrator* terminal so it runs while logged off):
REM     schtasks /Create /TN "ManuscriptDB Onboarding" ^
REM       /TR "C:\ManuscriptDB\run_onboarding_overnight.bat 2" ^
REM       /SC DAILY /ST 02:00 /F
REM  ...or just double-click register_onboarding_task.bat once.
REM
REM  PREREQUISITES (one-time):
REM   * Claude Code installed and logged in   (run `claude` once interactively)
REM   * FIRECRAWL_API_KEY available — either a persistent user env var, or put the
REM     key (one line, nothing else) in a file named  .firecrawl_key  in this folder
REM     (that file should NOT be committed to git).
REM   * .claude\settings.json allowlist (see WORKFLOW section 5) is recommended as a
REM     second layer even though we also pass --permission-mode bypassPermissions.
REM ============================================================================

setlocal
cd /d "%~dp0"

REM --- how many queue ranges to attempt this run -------------------------
set "BATCHES=%~1"
if "%BATCHES%"=="" set "BATCHES=2"

REM --- logging ------------------------------------------------------------
if not exist "logs" mkdir "logs"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set "TS=%%i"
set "LOG=%~dp0logs\onboarding_%TS%.log"

echo ====================================================================>> "%LOG%"
echo Run started %DATE% %TIME%   (up to %BATCHES% range(s)) >> "%LOG%"
echo ====================================================================>> "%LOG%"

REM --- Firecrawl key: env var, else read from .firecrawl_key -------------
if not defined FIRECRAWL_API_KEY (
    if exist "%~dp0.firecrawl_key" (
        set /p FIRECRAWL_API_KEY=<"%~dp0.firecrawl_key"
    )
)
if not defined FIRECRAWL_API_KEY (
    echo [error] FIRECRAWL_API_KEY not set and no .firecrawl_key file found. Aborting.>> "%LOG%"
    echo [error] FIRECRAWL_API_KEY not set and no .firecrawl_key file found. See header.
    endlocal & exit /b 1
)

REM --- make sure the tools exist -----------------------------------------
where claude >nul 2>nul
if errorlevel 1 (
    echo [error] 'claude' not on PATH. Install Claude Code and log in first.>> "%LOG%"
    endlocal & exit /b 1
)
where python >nul 2>nul
if errorlevel 1 (
    echo [error] 'python' not on PATH. Aborting.>> "%LOG%"
    endlocal & exit /b 1
)

REM --- nothing to do? -----------------------------------------------------
for /f %%c in ('python next_batch.py --count 2^>nul') do set "REMAIN=%%c"
echo Queue ranges remaining: %REMAIN% >> "%LOG%"
if "%REMAIN%"=="0" (
    echo Queue empty — nothing to onboard. Exiting.>> "%LOG%"
    endlocal & exit /b 0
)

REM --- the headless instruction ------------------------------------------
set "PROMPT=Run the onboarding loop from WORKFLOW-manuscript-onboarding.md section 8. Process up to %BATCHES% queue ranges this run, then stop. For each range: run `python next_batch.py --range-only` to get it (stop immediately if the queue is empty); sweep that range to a JSON; classify by Subjects; clean the Greek per section 3c; pick only well-preserved items; translate them faithfully line-by-line per section 3d; build .txt files with the line-count-asserting build script per section 3e; verify /api/manuscripts shows 0 parse errors and fix before proceeding; preserve scrape JSON for anything not built (rename to _PENDING_*.json); then run python next_batch.py --done with that range to tick it off. Before starting, check the Firecrawl credit balance and stop if it is low. Do not ask me for confirmation at any point."

echo Launching Claude Code (headless)...>> "%LOG%"
claude -p "%PROMPT%" --permission-mode bypassPermissions >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"

echo -------------------------------------------------------------------->> "%LOG%"
echo Run finished %DATE% %TIME%   exit code %RC% >> "%LOG%"
for /f %%c in ('python next_batch.py --count 2^>nul') do echo Ranges remaining now: %%c >> "%LOG%"

endlocal & exit /b %RC%
