"""
Pydantic Models - Request/Response schemas for all API endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# ─────────────────────────────────────────────────────────────────────────────
# AUTH MODELS
# ─────────────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    plan: str = "free"
    analyses_count: int = 0
    created_at: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# RESUME MODELS
# ─────────────────────────────────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    resume_id: str
    file_name: str
    raw_text: str
    word_count: int
    page_count: int
    parsed_data: Dict[str, Any]
    message: str = "Resume uploaded and parsed successfully"


class ParsedResume(BaseModel):
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    projects: List[str] = []
    technologies: List[str] = []
    contact_info: Dict[str, str] = {}
    sections_found: List[str] = []


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS MODELS
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    resume_id: str
    job_description: str = Field(..., min_length=50)
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class SkillMatchResult(BaseModel):
    skill: str
    matched: bool
    confidence: float = 1.0


class ScoreBreakdown(BaseModel):
    ats_score: float = Field(..., ge=0, le=100)
    keyword_match_pct: float = Field(..., ge=0, le=100)
    semantic_similarity: float = Field(..., ge=0, le=100)
    skill_overlap_pct: float = Field(..., ge=0, le=100)
    formatting_score: float = Field(..., ge=0, le=100)
    section_completeness: float = Field(..., ge=0, le=100)
    resume_quality_score: float = Field(..., ge=0, le=100)


class AISuggestions(BaseModel):
    missing_skills_tips: List[str] = []
    optimization_tips: List[str] = []
    better_bullet_points: List[str] = []
    action_verbs: List[str] = []
    ats_feedback: List[str] = []
    project_improvements: List[str] = []
    overall_summary: str = ""


class AnalysisResponse(BaseModel):
    analysis_id: str
    resume_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None

    # Scores
    scores: ScoreBreakdown

    # Skills
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    resume_skills: List[str] = []
    jd_required_skills: List[str] = []

    # Keywords
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []

    # AI
    ai_suggestions: AISuggestions

    # Meta
    status: str = "completed"
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# HISTORY / REPORT MODELS
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisSummary(BaseModel):
    id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    ats_score: float
    semantic_similarity: float
    created_at: datetime
    status: str


class HistoryResponse(BaseModel):
    analyses: List[AnalysisSummary]
    total: int


class ReportResponse(BaseModel):
    report_id: str
    analysis_id: str
    file_url: str
    file_name: str
    created_at: datetime


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK MODEL
# ─────────────────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    analysis_id: str
    focus_area: Optional[str] = "general"  # skills | bullets | ats | general
