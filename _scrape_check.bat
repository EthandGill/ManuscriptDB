@echo off
cd /d "%~dp0"
> _scrape_check.log echo === scrape diagnostic ===
python --version >> _scrape_check.log 2>&1
for /f %%L in ('powershell -NoProfile -Command "(\"\" + $env:FIRECRAWL_API_KEY).Length"') do echo FIRECRAWL_KEY_LEN=%%L >> _scrape_check.log
if exist "%~dp0.firecrawl_key" (echo FIRECRAWL_KEY_FILE=YES>> _scrape_check.log) else (echo FIRECRAWL_KEY_FILE=NO>> _scrape_check.log)
python -c "import firecrawl; print('firecrawl import OK')" >> _scrape_check.log 2>&1
python -c "import truststore; print('truststore import OK')" >> _scrape_check.log 2>&1
echo --- _sweep files present: >> _scrape_check.log
dir /b _sweep_*.json >> _scrape_check.log 2>&1
echo --- first 8 ranges in sweep_ranges.txt: >> _scrape_check.log
powershell -NoProfile -Command "Get-Content sweep_ranges.txt | Where-Object {$_ -and -not $_.StartsWith('#')} | Select-Object -First 8" >> _scrape_check.log 2>&1
echo DONE >> _scrape_check.log
