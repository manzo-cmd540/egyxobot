@echo off
chcp 65001 >nul

echo WARNING: This will delete the virtual environment!
set /p confirm="Are you sure? (y/n): "

if /i not "%confirm%"=="y" exit /b 0

echo Deleting...
rmdir /s /q venv 2>nul

echo [OK] Deleted!
echo Please run quick_setup.bat to create a new environment
pause