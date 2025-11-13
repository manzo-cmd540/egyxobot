@echo off
chcp 65001 >nul
echo ========================================
echo        Bot Check
echo ========================================
echo.

echo Checking files:
echo.

if exist "main_bot.py" (
    echo [OK] main_bot.py
) else (
    echo [ERROR] main_bot.py
)

if exist ".env" (
    echo [OK] .env
) else (
    echo [ERROR] .env (missing - copy .env.example)
)

if exist "requirements.txt" (
    echo [OK] requirements.txt
) else (
    echo [ERROR] requirements.txt
)

if exist "database\" (
    echo [OK] database folder
) else (
    echo [ERROR] database folder
)

if exist "handlers\" (
    echo [OK] handlers folder
) else (
    echo [ERROR] handlers folder
)

if exist "venv" (
    echo [OK] Virtual environment
) else (
    echo [WARNING] Virtual environment (run quick_setup.bat)
)

echo.
echo Python version:
python --version

echo.
echo ========================================
pause