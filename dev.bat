@echo off
chcp 65001 >nul

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

set PYTHONUNBUFFERED=1
set DEBUG=1

echo Development mode enabled
echo.

python -u main_bot.py
pause