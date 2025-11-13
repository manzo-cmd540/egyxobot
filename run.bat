@echo off
chcp 65001 >nul

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run quick_setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python main_bot.py
pause