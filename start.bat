@echo off
rem Notes: one-click start on Windows. Double-click this file.
cd /d "%~dp0"

rem .venv copied from macOS/Linux does not work on Windows - recreate it
if exist ".venv" if not exist ".venv\Scripts\python.exe" (
  echo Removing .venv made on another OS...
  rmdir /s /q ".venv"
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv 2>/dev/null || python -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo Python not found. Install it from https://www.python.org/downloads/
  echo and check "Add python.exe to PATH" during installation.
  pause
  exit /b 1
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r backend\requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies. Check the internet connection.
  pause
  exit /b 1
)

rem open the browser after the server has had a moment to start
if not defined NOTES_NO_BROWSER start "" cmd /c "ping -n 4 127.0.0.1 >/dev/null & start http://localhost:8000"
echo.
echo Server: http://localhost:8000  (close this window to stop)
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
