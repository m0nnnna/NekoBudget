@echo off
echo ========================================
echo NekoBudget Build Script
echo ========================================
echo.

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Building NekoBudget.exe...
echo.

:: Build the executable
pyinstaller --onefile --windowed --name NekoBudget --icon=NONE --add-data "database.py;." main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo Executable located at: dist\NekoBudget.exe
    echo ========================================
) else (
    echo.
    echo Build failed!
)

pause
