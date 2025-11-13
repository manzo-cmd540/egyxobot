@echo off
chcp 65001 >nul

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Updating pip...
python -m pip install --upgrade pip -q

echo Updating libraries...
pip install -r requirements.txt --upgrade -q

echo [OK] Update completed!
pause