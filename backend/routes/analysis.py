"""
Analysis Routes - Core ATS scoring engine endpoint
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from loguru import logger

from backend.auth.jwt_handler import get_current_user
from backend.models.schemas import AnalysisRequest, AnalysisResponse, ScoreBreakdown, AISuggestions
from backend.nlp.nlp_pipeline import (
    parse_resume, parse_job_description,
    compute_semantic_similarity, compute_tfidf_similarity, compute_ats_score
)
from backend.services.groq_service import generate_resume_suggestions, compute_interview_readiness
from backend.database.supabase_client import get_supabase

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def analyze_resume(
    body: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """Full ATS analysis: NLP scoring + Groq AI suggestions."""
    supabase = get_supabase()
    analysis_id = str(uuid.uuid4())

    try:
        # ── 1. Fetch resume ─────────────────────────────────────────────
        resume_res = (
            supabase.table("resumes")
            .select("*")
            .eq("id", body.resume_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )
        if not resume_res.data:
            raise HTTPException(status_code=404, detail="Resume not found")
        resume = resume_res.data
        resume_text = resume.get("raw_text", "")
        parsed_resume = resume.get("parsed_data", {})
        resume_skills = parsed_resume.get("skills", [])

        # ── 2. Parse JD ─────────────────────────────────────────────────
        jd_parsed = parse_job_description(body.job_description)
        jd_skills = jd_parsed.get("required_skills", [])

        # ── 3. Compute similarities ──────────────────────────────────────
        semantic_sim = compute_semantic_similarity(resume_text, body.job_description)
        tfidf_sim    = compute_tfidf_similarity(resume_text, body.job_description)

        # ── 4. ATS Score ─────────────────────────────────────────────────
        sections_dict = {s: "" for s in parsed_resume.get("sections", [])}
        scores = compute_ats_score(
            resume_text=resume_text,
            jd_text=body.job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            sections=sections_dict,
            semantic_sim=semantic_sim,
            tfidf_sim=tfidf_sim,
        )

        # ── 5. Groq AI Suggestions ────────────────────────────────────────
        ai_raw = generate_resume_suggestions(
            resume_text=resume_text,
            job_description=body.job_description,
            matched_skills=scores["matched_skills"],
            missing_skills=scores["missing_skills"],
            missing_keywords=scores["missing_keywords"],
            ats_score=scores["ats_score"],
        )
        ai_suggestions = AISuggestions(**ai_raw)

        # ── 6. Save to DB ─────────────────────────────────────────────────
        record = {
            "id":                   analysis_id,
            "user_id":              current_user["id"],
            "resume_id":            body.resume_id,
            "job_title":            body.job_title,
            "company_name":         body.company_name,
            "job_description":      body.job_description[:10000],
            "ats_score":            scores["ats_score"],
            "keyword_match_pct":    scores["keyword_match_pct"],
            "semantic_similarity":  scores["semantic_similarity"],
            "skill_overlap_pct":    scores["skill_overlap_pct"],
            "formatting_score":     scores["formatting_score"],
            "section_completeness": scores["section_completeness"],
            "resume_quality_score": scores["resume_quality_score"],
            "matched_skills":       scores["matched_skills"],
            "missing_skills":       scores["missing_skills"],
            "matched_keywords":     scores["matched_keywords"],
            "missing_keywords":     scores["missing_keywords"],
            "jd_required_skills":   jd_skills,
            "resume_skills":        resume_skills,
            "ai_suggestions":       ai_raw,
            "status":               "completed",
        }
        supabase.table("analyses").insert(record).execute()

        # Increment user's analysis count
        count = current_user.get("analyses_count", 0) + 1
        supabase.table("profiles").update({"analyses_count": count}).eq("id", current_user["id"]).execute()

        logger.info(f"Analysis {analysis_id} completed — ATS score: {scores['ats_score']}")

        return AnalysisResponse(
            analysis_id=analysis_id,
            resume_id=body.resume_id,
            job_title=body.job_title,
            company_name=body.company_name,
            scores=ScoreBreakdown(
                ats_score=scores["ats_score"],
                keyword_match_pct=scores["keyword_match_pct"],
                semantic_similarity=scores["semantic_similarity"],
                skill_overlap_pct=scores["skill_overlap_pct"],
                formatting_score=scores["formatting_score"],
                section_completeness=scores["section_completeness"],
                resume_quality_score=scores["resume_quality_score"],
            ),
            matched_skills=scores["matched_skills"],
            missing_skills=scores["missing_skills"],
            resume_skills=resume_skills,
            jd_required_skills=jd_skills,
            matched_keywords=scores["matched_keywords"],
            missing_keywords=scores["missing_keywords"],
            ai_suggestions=ai_suggestions,
            status="completed",
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        supabase.table("analyses").insert({
            "id": analysis_id, "user_id": current_user["id"],
            "resume_id": body.resume_id, "job_description": body.job_description[:500],
            "status": "failed", "error_message": str(e),
        }).execute()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a specific analysis by ID."""
    supabase = get_supabase()
    result = (
        supabase.table("analyses")
        .select("*")
        .eq("id", analysis_id)
        .eq("user_id", current_user["id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result.data


@router.post("/feedback")
async def generate_feedback(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Regenerate AI feedback for an existing analysis."""
    supabase = get_supabase()
    result = (
        supabase.table("analyses").select("*")
        .eq("id", analysis_id).eq("user_id", current_user["id"])
        .single().execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = result.data
    resume_res = supabase.table("resumes").select("raw_text").eq("id", analysis["resume_id"]).single().execute()
    resume_text = resume_res.data.get("raw_text", "") if resume_res.data else ""

    ai_raw = generate_resume_suggestions(
        resume_text=resume_text,
        job_description=analysis.get("job_description", ""),
        matched_skills=analysis.get("matched_skills", []),
        missing_skills=analysis.get("missing_skills", []),
        missing_keywords=analysis.get("missing_keywords", []),
        ats_score=analysis.get("ats_score", 0),
    )

    supabase.table("analyses").update({"ai_suggestions": ai_raw}).eq("id", analysis_id).execute()
    return {"ai_suggestions": ai_raw, "message": "Feedback regenerated"}
