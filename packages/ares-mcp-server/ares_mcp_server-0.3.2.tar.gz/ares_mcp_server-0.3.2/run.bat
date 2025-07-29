@echo off
REM ARES MCP Server - Automated Setup and Run Script for Windows
REM This script will set up the virtual environment, install dependencies, and run the server

setlocal enabledelayedexpansion

REM Colors (using echo with escape sequences)
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "NC=[0m"

REM Print functions
echo ==========================================
echo   ARES MCP Server Setup ^& Run
echo ==========================================
echo.

REM Check if Python 3 is installed
echo [ARES MCP] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [ARES MCP] Python %PYTHON_VERSION% detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [ARES MCP] Creating virtual environment...
    python -m venv venv
    echo [ARES MCP] Virtual environment created
) else (
    echo [ARES MCP] Virtual environment already exists
)

REM Activate virtual environment
echo [ARES MCP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install or update dependencies
echo [ARES MCP] Checking dependencies...
pip show mcp >nul 2>&1
if errorlevel 1 (
    echo [ARES MCP] Installing dependencies...
    pip install -r requirements.txt
    echo [ARES MCP] Dependencies installed
) else (
    echo [ARES MCP] Core dependencies already installed
    set /p UPDATE="Do you want to update dependencies? (y/N) "
    if /i "!UPDATE!"=="y" (
        echo [ARES MCP] Updating dependencies...
        pip install -U -r requirements.txt
        echo [ARES MCP] Dependencies updated
    )
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo [ARES MCP] Creating .env configuration file...
    copy .env.example .env >nul
    echo [ARES MCP] .env file created
    echo [WARNING] You can edit .env to customize server settings
) else (
    echo [ARES MCP] Configuration file already exists
)

echo.
echo [ARES MCP] Setup completed successfully!
echo.

REM Ask if user wants to run the server
set /p RUN="Do you want to start the server now? (Y/n) "
if /i not "!RUN!"=="n" (
    echo.
    echo ==========================================
    echo   ARES MCP Server is starting...
    echo   Press Ctrl+C to stop the server
    echo ==========================================
    echo.
    python -m ares_mcp_server.server
) else (
    echo [ARES MCP] Setup complete. To run the server later, use:
    echo   venv\Scripts\activate
    echo   python -m ares_mcp_server.server
)

pause