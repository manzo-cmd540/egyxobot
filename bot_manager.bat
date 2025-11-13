@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:menu
cls
echo.
echo ========================================
echo      Smart Bot Manager
echo ========================================
echo.
echo Options:
echo.
echo   1. Setup (First Time)
echo      - Create virtual environment
echo      - Install libraries
echo      - Create database
echo.
echo   2. Run Bot (Normal)
echo      - Start bot normally
echo      - Production mode
echo.
echo   3. Development Mode
echo      - Show detailed errors
echo      - Debug information
echo.
echo   4. Telegram Login
echo      - Register personal account
echo      - For uploading large files
echo.
echo   5. Clean Files
echo      - Delete temporary files
echo      - Free up space
echo.
echo   6. Install FFmpeg
echo      - For watermarks
echo      - For videos and images
echo.
echo   7. Show Logs
echo      - View error logs
echo.
echo   8. Update Libraries
echo      - Update pip and libraries
echo      - Fix issues
echo.
echo   0. Exit
echo.
echo ========================================
set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto run
if "%choice%"=="3" goto dev_mode
if "%choice%"=="4" goto login
if "%choice%"=="5" goto clean
if "%choice%"=="6" goto install_ffmpeg
if "%choice%"=="7" goto show_logs
if "%choice%"=="8" goto update_deps
if "%choice%"=="0" goto exit_app
goto menu

REM ========================================
REM 1. Setup
REM ========================================
:setup
cls
echo ========================================
echo      Bot Setup
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Download from: https://www.python.org/downloads/
    pause
    goto menu
)

echo [OK] Python found

if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Updating pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo Installing libraries...
pip install -r requirements.txt

echo.
echo Installing Playwright...
python -m playwright install chromium >nul 2>&1

echo.
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file with your data
    echo You can copy .env.example to .env
) else (
    echo [OK] .env file found
)

echo.
echo Creating database...
python database/db_init.py

echo.
echo ========================================
echo [OK] Setup completed!
echo ========================================
echo.
echo Next steps:
echo   1. Check .env file
echo   2. Choose option 2 to run bot
echo.
pause
goto menu

REM ========================================
REM 2. Run Bot
REM ========================================
:run
cls
echo ========================================
echo       Running Smart Bot
echo ========================================
echo.

if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file first
    echo.
    pause
    goto menu
)

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please choose option 1 for setup
    echo.
    pause
    goto menu
)

call venv\Scripts\activate.bat

echo.
echo ========================================
echo [OK] Bot is running...
echo Press Ctrl+C to stop
echo ========================================
echo.

python main_bot.py

echo.
echo Bot stopped
pause
goto menu

REM ========================================
REM 3. Development Mode
REM ========================================
:dev_mode
cls
echo ========================================
echo      Development Mode
echo ========================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    pause
    goto menu
)

call venv\Scripts\activate.bat

set PYTHONUNBUFFERED=1

echo.
echo ========================================
echo Development mode enabled
echo You will see detailed error messages
echo Press Ctrl+C to stop
echo ========================================
echo.

python -u main_bot.py

echo.
echo Bot stopped
pause
goto menu

REM ========================================
REM 4. Telegram Login
REM ========================================
:login
cls
echo ========================================
echo   Telegram Login (Telethon)
echo ========================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    pause
    goto menu
)

call venv\Scripts\activate.bat

echo.
echo IMPORTANT WARNINGS:
echo   - Save the verification code safely
echo   - Connection may take some time
echo   - If you have 2FA, you will need password
echo.

pause

echo.
echo ========================================
echo Starting login...
echo ========================================
echo.

python handlers/account_handler.py

echo.
echo Login completed
echo.
pause
goto menu

REM ========================================
REM 5. Clean Files
REM ========================================
:clean
cls
echo ========================================
echo        Clean Temporary Files
echo ========================================
echo.

set /p confirm="Are you sure? Delete temporary files? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo.
echo Starting cleanup...

for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo Deleting: %%d
        rmdir /s /q "%%d"
    )
)

for /r . %%f in (*.pyc) do (
    if exist "%%f" (
        echo Deleting: %%f
        del "%%f"
    )
)

for /d /r . %%d in (*.egg-info) do (
    if exist "%%d" (
        echo Deleting: %%d
        rmdir /s /q "%%d"
    )
)

if exist ".pytest_cache" (
    echo Deleting: .pytest_cache
    rmdir /s /q ".pytest_cache"
)

if exist "temp" (
    echo Deleting: temp
    rmdir /s /q "temp"
)

if exist "images" (
    echo Deleting: images
    rmdir /s /q "images"
)

echo.
echo ========================================
echo [OK] Cleanup completed!
echo ========================================
echo.
pause
goto menu

REM ========================================
REM 6. Install FFmpeg
REM ========================================
:install_ffmpeg
cls
echo ========================================
echo           Install FFmpeg
echo ========================================
echo.

ffmpeg -version >nul 2>&1
if errorlevel 0 (
    echo [OK] FFmpeg is already installed
    ffmpeg -version | find "version"
    echo.
    pause
    goto menu
)

echo ERROR: FFmpeg is not installed
echo.
echo Installation options:
echo   1. Using Chocolatey (Easiest)
echo   2. Manual download
echo.

set /p ffmpeg_choice="Choose option (1 or 2): "

if "%ffmpeg_choice%"=="1" (
    choco --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Chocolatey is not installed
        echo Download from: https://chocolatey.org/install
        echo.
        pause
        goto menu
    )
    
    echo.
    echo Installing FFmpeg via Chocolatey...
    choco install ffmpeg -y
    
    echo.
    echo [OK] Installation completed!
    pause
    goto menu
)

if "%ffmpeg_choice%"=="2" (
    echo.
    echo Please download FFmpeg manually from:
    echo    https://ffmpeg.org/download.html
    echo.
    echo After installation:
    echo   1. Add FFmpeg path to environment variables
    echo   2. Restart your computer
    echo   3. Test: ffmpeg -version
    echo.
    pause
    goto menu
)

goto menu

REM ========================================
REM 7. Show Logs
REM ========================================
:show_logs
cls
echo ========================================
echo            Recent Logs
echo ========================================
echo.

if not exist "bot.log" (
    echo ERROR: Log file not found
    pause
    goto menu
)

echo Last 50 lines of log:
echo.
for /f "skip=1" %%a in ('find /c /v "" "bot.log"') do set lines=%%a
if %lines% GTR 50 (
    for /f "tokens=*" %%a in ('more +%lines%-50 "bot.log"') do echo %%a
) else (
    type bot.log
)

echo.
pause
goto menu

REM ========================================
REM 8. Update Libraries
REM ========================================
:update_deps
cls
echo ========================================
echo         Update Libraries
echo ========================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please choose option 1 for setup
    pause
    goto menu
)

call venv\Scripts\activate.bat

echo Updating pip...
python -m pip install --upgrade pip -q

echo Updating libraries...
pip install -r requirements.txt --upgrade -q

echo.
echo ========================================
echo [OK] Update completed!
echo ========================================
echo.
pause
goto menu

REM ========================================
REM Exit
REM ========================================
:exit_app
echo.
echo Goodbye!
echo.
exit /b 0