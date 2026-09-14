@echo off
set "CHP_APP_ROOT=%~dp0"
cd /d "%CHP_APP_ROOT%"
set "CHP_ANTIGRAVITY_CLI="
if exist "%HOMEDRIVE%%HOMEPATH%\AppData\Local\agy\bin\agy.exe" set "CHP_ANTIGRAVITY_CLI=%HOMEDRIVE%%HOMEPATH%\AppData\Local\agy\bin\agy.exe"
if not defined CHP_ANTIGRAVITY_CLI if exist "%USERPROFILE%\AppData\Local\agy\bin\agy.exe" set "CHP_ANTIGRAVITY_CLI=%USERPROFILE%\AppData\Local\agy\bin\agy.exe"
if not defined CHP_ANTIGRAVITY_CLI if exist "%LOCALAPPDATA%\agy\bin\agy.exe" set "CHP_ANTIGRAVITY_CLI=%LOCALAPPDATA%\agy\bin\agy.exe"
if defined CHP_ANTIGRAVITY_CLI (
  if not exist "data" mkdir "data"
  >"data\antigravity-cli.path" echo %CHP_ANTIGRAVITY_CLI%
)
if exist "%CHP_APP_ROOT%.venv\Scripts\python.exe" (
  "%CHP_APP_ROOT%.venv\Scripts\python.exe" -m chp.launcher %*
) else (
  py -3 -m chp.launcher %*
)
if errorlevel 1 pause
