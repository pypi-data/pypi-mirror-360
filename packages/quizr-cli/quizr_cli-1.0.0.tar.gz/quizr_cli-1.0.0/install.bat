@echo off
echo ========================================
echo       QUIZR Installation Script
echo ========================================
echo.
echo This will install QUIZR and its dependencies.
echo.
pause

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing QUIZR...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install QUIZR
    pause
    exit /b 1
)

echo.
echo ========================================
echo      Installation Complete!
echo ========================================
echo.
echo You can now use QUIZR with:
echo   python -m quizr list
echo   python -m quizr start network+ quick
echo   python -m quizr progress
echo.
echo Testing installation...
python -m quizr --help >nul 2>&1
if errorlevel 1 (
    echo WARNING: Installation may have issues
) else (
    echo ✓ QUIZR installed successfully!
)

echo.
pause 