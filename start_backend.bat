@echo off
echo ==========================================
echo  ATS Resume Scorer - Starting Backend
echo ==========================================
cd /d "%~dp0"

set "VENV_DIR=.venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" set "VENV_DIR=venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    set "VENV_DIR=.venv"
)

call "%VENV_DIR%\Scripts\activate.bat"

if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and fill in your API keys.
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo Downloading spaCy model...
python -m spacy download en_core_web_md --quiet 2>nul || (
    python -m spacy download en_core_web_sm --quiet 2>nul
)

echo.
echo Starting FastAPI backend on http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
