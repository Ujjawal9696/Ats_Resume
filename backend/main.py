"""
ATS Resume Scorer - FastAPI Main Application
Production-ready backend with full routing
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
import sys
import os

from backend.config import settings
from backend.database.supabase_client import init_supabase
from backend.routes import resume, analysis, auth, report, history

# ── Logging Setup ─────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add("logs/ats_scorer.log", rotation="10 MB", retention="7 days", level="DEBUG")

# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 ATS Resume Scorer API starting up...")
    init_supabase()
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logger.info("✅ All services initialized")
    yield
    logger.info("🛑 ATS Resume Scorer API shutting down...")

# ── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="ATS Resume Scorer API",
    description="""
    ## 🎯 AI-Powered ATS Resume Analyzer

    A production-ready API for analyzing resumes against job descriptions using:
    - **NLP**: spaCy + Sentence Transformers + TF-IDF
    - **LLM**: Groq API (Llama 3)
    - **Auth**: Supabase JWT + Google OAuth
    - **Storage**: Supabase Storage + PostgreSQL
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/auth",    tags=["🔐 Authentication"])
app.include_router(resume.router,   prefix="/resume",  tags=["📄 Resume"])
app.include_router(analysis.router, prefix="/analyze", tags=["🧠 Analysis"])
app.include_router(report.router,   prefix="/report",  tags=["📊 Reports"])
app.include_router(history.router,  prefix="/history", tags=["📋 History"])

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["🏥 Health"])
async def root():
    return {
        "status": "healthy",
        "service": "ATS Resume Scorer API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health", tags=["🏥 Health"])
async def health():
    return {"status": "ok", "uptime": "running"}

# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
