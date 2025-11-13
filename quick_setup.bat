@echo off
chcp 65001 >nul
echo ========================================
echo      Quick Setup - Smart Bot
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing libraries...
pip install -r requirements.txt -q

echo Installing Playwright...
python -m playwright install chromium -q

echo Creating database...
python database/db_init.py

echo.
echo ========================================
echo [OK] Setup completed!
echo ========================================
echo.
echo Now use: bot_manager.bat
echo.
pause