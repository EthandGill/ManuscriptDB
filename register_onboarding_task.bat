@echo off
REM ============================================================================
REM  register_onboarding_task.bat  —  one-click Task Scheduler setup
REM ----------------------------------------------------------------------------
REM  Registers a daily 2:00 AM task that runs run_onboarding_overnight.bat.
REM  RIGHT-CLICK this file and choose "Run as administrator" so the task can run
REM  even when you're logged off.
REM
REM  To change the time, edit /ST below (24-hour HH:MM). To process more ranges
REM  per night, change the "2" in the /TR line.
REM  To remove it later:  schtasks /Delete /TN "ManuscriptDB Onboarding" /F
REM ============================================================================

set "TASKNAME=ManuscriptDB Onboarding"
set "RUNNER=%~dp0run_onboarding_overnight.bat"

echo Registering scheduled task "%TASKNAME%"
echo   command: "%RUNNER%" 2
echo   when:    daily at 02:00
echo.

schtasks /Create ^
  /TN "%TASKNAME%" ^
  /TR "\"%RUNNER%\" 2" ^
  /SC DAILY ^
  /ST 02:00 ^
  /F

if errorlevel 1 (
    echo.
    echo [error] Could not create the task. Re-run this file as Administrator.
    echo         ^(Right-click ^> Run as administrator.^)
) else (
    echo.
    echo Done. It will run nightly at 2:00 AM. Logs land in  %~dp0logs\.
    echo Run it now to test:   schtasks /Run /TN "%TASKNAME%"
    echo Remove it later:      schtasks /Delete /TN "%TASKNAME%" /F
)
echo.
pause
