@echo off
REM Keylogger POC Uninstallation Script for Windows
REM Educational Purpose Only - Use Responsibly

echo ========================================
echo Keylogger POC Uninstallation Script
echo Educational Purpose Only
echo ========================================
echo.

echo WARNING: This will remove all keylogger files and logs!
echo.
set /p confirm="Are you sure you want to continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo Stopping any running keylogger processes...

REM Kill any running Python processes that might be the keylogger
tasklist /fi "imagename eq python.exe" | find /i "python.exe" >nul
if not errorlevel 1 (
    echo Found running Python processes. Attempting to stop keylogger...
    REM Create kill switch file
    echo. > KILL_SWITCH
    timeout /t 5 /nobreak >nul
    del KILL_SWITCH 2>nul
)

REM Remove startup persistence
echo Removing startup persistence...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSecurityUpdate" /f >nul 2>&1
if not errorlevel 1 (
    echo Startup persistence removed.
) else (
    echo No startup persistence found.
)

REM Ask about log files
echo.
set /p remove_logs="Do you want to remove all log files? (y/N): "
if /i "%remove_logs%"=="y" (
    echo Removing log files...
    if exist "logs" (
        rmdir /s /q "logs"
        echo Log files removed.
    ) else (
        echo No log files found.
    )
) else (
    echo Log files preserved.
)

REM Ask about configuration
echo.
set /p remove_config="Do you want to remove configuration files? (y/N): "
if /i "%remove_config%"=="y" (
    echo Removing configuration files...
    if exist "config.ini" del "config.ini"
    if exist ".encryption_key" del ".encryption_key"
    if exist ".encryption_key.bak" del ".encryption_key.bak"
    echo Configuration files removed.
) else (
    echo Configuration files preserved.
)

REM Ask about Python packages
echo.
set /p remove_packages="Do you want to uninstall Python packages? (y/N): "
if /i "%remove_packages%"=="y" (
    echo Uninstalling Python packages...
    pip uninstall -y pynput cryptography requests Pillow psutil pywin32 pywin32-ctypes schedule python-dateutil colorama tqdm
    echo Python packages uninstalled.
) else (
    echo Python packages preserved.
)

echo.
echo ========================================
echo Uninstallation completed!
echo ========================================
echo.
echo The keylogger has been removed from your system.
echo.
echo If you preserved log files or configuration,
echo you can find them in the current directory.
echo.
pause

