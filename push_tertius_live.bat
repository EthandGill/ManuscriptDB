@echo off
REM One-off: publish the Tertius agent + live progress badge to the website.
cd /d "%~dp0"
set FILES=app.py templates/index.html static/style.css static/tertius_badge.js static/data/tertius_progress.json .gitignore CLAUDE.md tertius.py tertius_widget.py Tertius.bat TERTIUS-agent.md push_tertius_live.bat
echo Publishing Tertius to the live site...
git add %FILES%
git commit -m "Add Tertius translating agent + live progress badge" -- %FILES%
git push
if errorlevel 1 goto failed
echo.
echo DONE - Railway will redeploy in a minute or two.
pause
exit /b 0
:failed
echo.
echo PUSH FAILED - see above
pause
