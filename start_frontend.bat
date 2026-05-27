@echo off
echo ==========================================
echo  ATS Resume Scorer - Starting Frontend
echo ==========================================
cd /d "%~dp0"

set "VENV_DIR=.venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" set "VENV_DIR=venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run start_backend.bat first to set up the environment.
    pause
    exit /b 1
)

if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and fill in your API keys.
    pause
    exit /b 1
)

echo.
echo Starting Streamlit frontend on http://localhost:8501
echo.
start "ATS Frontend" cmd /k "cd /d \"%~dp0\" && call \"%VENV_DIR%\Scripts\activate.bat\" && python -m streamlit run frontend/streamlit_app.py --server.port 8501 --server.address localhost --theme.base dark --browser.gatherUsageStats false"

timeout /t 3 /nobreak >nul
start "" http://localhost:8501
echo Opened the browser at http://localhost:8501
