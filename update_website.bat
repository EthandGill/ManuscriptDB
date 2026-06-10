@echo off
REM ============================================================
REM  Push your local changes live. Double-click to update the
REM  website (https://manuscriptdb.org). Railway redeploys
REM  automatically about a minute after the push.
REM ============================================================

cd /d "%~dp0"

echo.
echo  Checking for changes...
git add -A

REM Show what changed
git status --short

echo.
set /p msg="Short description of your change (press Enter for 'Update site'): "
if "%msg%"=="" set msg=Update site

git commit -m "%msg%"
if errorlevel 1 (
  echo.
  echo  Nothing new to commit - your live site already matches your files.
  echo.
  pause
  exit /b
)

echo.
echo  Pushing to GitHub (Railway will auto-deploy)...
git push

echo.
echo ============================================================
if errorlevel 1 (
  echo  Push failed. Copy the error text above and send it to Claude.
) else (
  echo  Pushed! Railway is rebuilding now.
  echo  In ~1-2 min, refresh https://manuscriptdb.org to see changes.
)
echo ============================================================
pause
