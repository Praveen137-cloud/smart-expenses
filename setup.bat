@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Smart Expense Tracker - First-time Setup

echo ========================================
echo  First-time Setup
echo ========================================
echo.

echo [1/5] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found. Install Python 3.11+ from https://www.python.org
    goto :fail
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python 3.11 or newer is required. & goto :fail )

echo [2/5] Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 ( echo [ERROR] Could not create the virtual environment. & goto :fail )
)
call ".venv\Scripts\activate.bat"

echo [3/5] Installing dependencies...
python -m pip install --disable-pip-version-check -r "backend\requirements.txt"
if errorlevel 1 ( echo [ERROR] Dependency installation failed. & goto :fail )
echo ok> ".venv\.deps_installed"

echo [4/5] Configuring .env...
if not exist ".env" copy /y ".env.example" ".env" >nul
echo Opening .env - set DB_USER and DB_PASSWORD for your MySQL, save, then close Notepad.
notepad ".env"

echo [5/5] Training ML model...
python "backend\train_classifier.py"
if errorlevel 1 ( echo [ERROR] Model training failed. & goto :fail )

echo.
echo ========================================
echo  Setup complete
echo ========================================
echo.
echo DATABASE SETUP (do this once):
echo   1. Make sure MySQL 8+ is running.
echo   2. In MySQL Workbench or the MySQL command line run:
echo        SOURCE database/finance_db.sql;
echo      (Workbench: File ^> Run SQL Script... ^> choose database\finance_db.sql)
echo.
echo START THE APP:   double-click start.bat
echo.
pause
goto :end

:fail
echo.
echo Setup failed. See the message above.
pause
exit /b 1

:end
endlocal
