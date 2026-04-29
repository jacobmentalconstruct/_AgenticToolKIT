@echo off
echo === .dev-tools environment setup ===

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found on PATH.
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Environment ready.
