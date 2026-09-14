@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Open start.bat to launch CHP Knowledge Builder.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.12 or later with the Python launcher, then retry. Package installation also needs internet access.
pause
exit /b 1
