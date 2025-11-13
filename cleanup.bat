@echo off
chcp 65001 >nul
echo Cleaning temporary files...

for /d /r . %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do del "%%f" 2>nul
if exist "temp" rmdir /s /q "temp" 2>nul
if exist "images" rmdir /s /q "images" 2>nul

echo [OK] Cleanup completed!
echo.
pause