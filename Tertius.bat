@echo off
REM Tertius - the translating agent. Double-click to start; a pop-up appears on your desktop.
REM The console starts minimised (it holds the log). Use the stop button on the pop-up to finish cleanly.
cd /d "%~dp0"
start "Tertius" /min py tertius.py %*
