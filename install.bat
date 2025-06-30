@echo off
echo Installing Spring Boot Unit Test Generator Dependencies
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    echo Please ensure pip is installed and try again
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo =====================================================
echo Installation completed successfully!
echo =====================================================
echo.
echo Next steps:
echo 1. Set your Google Gemini AI API key:
echo    set GEMINI_API_KEY=your-api-key-here
echo.
echo 2. Run the tool:
echo    python main.py --help
echo.
echo 3. Or try the examples:
echo    python examples.py
echo.
pause
