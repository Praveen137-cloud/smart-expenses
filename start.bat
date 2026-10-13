@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Smart Expense and Finance Tracker

echo ========================================
echo  Smart Expense ^& Finance Tracker
echo ========================================
echo.

echo Checking Python...
if exist ".venv\Scripts\python.exe" (
    call ".venv\Scripts\activate.bat"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        echo Creating virtual environment with Python launcher...
        py -3.12 -m venv .venv 2>nul || py -3 -m venv .venv
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Python was not found. Install Python 3.11+ from https://www.python.org
            goto :fail
        )
        echo Creating virtual environment...
        python -m venv .venv
    )
    if not exist ".venv\Scripts\python.exe" ( echo [ERROR] Could not create the virtual environment. & goto :fail )
    call ".venv\Scripts\activate.bat"
)
if errorlevel 1 ( echo [ERROR] Could not activate the virtual environment. & goto :fail )

if not exist ".venv\.deps_installed" (
    echo Installing dependencies...
    python -m pip install --disable-pip-version-check -r "backend\requirements.txt"
    if errorlevel 1 ( echo [ERROR] Dependency installation failed. Check your internet connection. & goto :fail )
    echo ok> ".venv\.deps_installed"
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy /y ".env.example" ".env" >nul
    echo.
    echo [ACTION NEEDED] Open .env and set DB_PASSWORD to your MySQL password.
    notepad ".env"
)

echo Checking ML model...
if not exist "backend\model\expense_classifier.pkl" (
    echo Training ML model...
    python "backend\train_classifier.py"
    if errorlevel 1 ( echo [ERROR] Model training failed. & goto :fail )
)

echo Starting FastAPI server...
echo.
echo Application:  http://127.0.0.1:8000
echo API docs:     http://127.0.0.1:8000/docs
echo Press Ctrl+C to stop the server.
echo.

rem Open the browser once (outside uvicorn, so reloads never open extra tabs).
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://127.0.0.1:8000'"

python -m uvicorn backend.server:app --reload --reload-dir backend --reload-dir frontend --host 127.0.0.1 --port 8000
if errorlevel 1 ( echo [ERROR] The server stopped with an error. & goto :fail )
goto :end

:fail
echo.
echo Startup failed. See the message above.
pause
exit /b 1

:end
endlocal
