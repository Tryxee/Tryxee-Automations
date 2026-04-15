@echo off
setlocal enabledelayedexpansion

echo.
echo  ========================================
echo   Tryxee Automations - Build Script
echo  ========================================
echo.

:: Step 1: Install requirements
echo [1/3] Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Failed to install requirements. Aborting.
    pause
    exit /b 1
)
echo  Done.
echo.

:: Step 2: Clean old build artifacts
echo [2/3] Cleaning old build folders...
if exist "dist" (
    rmdir /s /q "dist"
    echo  Deleted: dist\
)
if exist "build" (
    rmdir /s /q "build"
    echo  Deleted: build\
)
echo  Done.
echo.

:: Step 3: Run PyInstaller
echo [3/3] Running PyInstaller...
echo.
pyinstaller "Tryxee Automations.spec" --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] PyInstaller failed. Check output above.
    pause
    exit /b 1
)

echo.
echo  ========================================
echo   Build complete! Output is in dist\
echo  ========================================
echo.
pause