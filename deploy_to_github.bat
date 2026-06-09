@echo off
REM ============================================================
REM  One-click: push ManuscriptDB to GitHub
REM  Just double-click this file. If a GitHub sign-in window
REM  pops up, click Authorize / sign in - then it finishes.
REM ============================================================

cd /d "%~dp0"

REM --- Check git is installed -------------------------------
where git >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Git is not installed. Download it from:
  echo      https://git-scm.com/download/win
  echo  Install with the default options, then double-click this file again.
  echo.
  pause
  exit /b
)

echo.
echo  Cleaning any previous git state...
if exist ".git" rmdir /s /q ".git"

echo  Initializing repository...
git init
git config user.email "Ethandgiller@gmail.com"
git config user.name "Ethan Gill"

> .gitignore echo __pycache__/
>> .gitignore echo *.pyc
>> .gitignore echo .DS_Store

echo  Staging files...
git add .

echo  Committing...
git commit -m "Deploy ManuscriptDB"

git branch -M main
git remote add origin https://github.com/EthandGill/ManuscriptDB.git

echo.
echo  Pushing to GitHub  (a sign-in window may open - approve it)...
git push -u origin main

echo.
echo ============================================================
if errorlevel 1 (
  echo  Something went wrong above. Copy the red/error text and
  echo  send it to Claude.
) else (
  echo  Done. Refresh https://github.com/EthandGill/ManuscriptDB
  echo  - your files should now be there.
)
echo ============================================================
pause
