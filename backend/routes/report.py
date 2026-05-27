"""
Report Routes - Generate and download PDF ATS analysis reports
"""

import uuid
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from loguru import logger

from backend.auth.jwt_handler import get_current_user
from backend.database.supabase_client import get_supabase
from backend.services.report_generator import generate_pdf_report

router = APIRouter()

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.get("/{analysis_id}/generate")
async def generate_report(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Generate a PDF report for an analysis."""
    supabase = get_supabase()

    # Fetch analysis
    result = (
        supabase.table("analyses").select("*")
        .eq("id", analysis_id).eq("user_id", current_user["id"])
        .single().execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    analysis = result.data

    # Fetch resume
    resume_res = (
        supabase.table("resumes").select("file_name, word_count")
        .eq("id", analysis.get("resume_id", "")).single().execute()
    )
    resume_meta = resume_res.data or {}

    try:
        report_id = str(uuid.uuid4())
        file_name = f"ats_report_{analysis_id[:8]}.pdf"
        file_path = os.path.join(REPORTS_DIR, file_name)

        generate_pdf_report(
            analysis=analysis,
            resume_meta=resume_meta,
            user=current_user,
            output_path=file_path,
        )

        # Save report record
        supabase.table("reports").insert({
            "id": report_id,
            "analysis_id": analysis_id,
            "user_id": current_user["id"],
            "file_name": file_name,
            "file_url": f"/report/{analysis_id}/download/{file_name}",
        }).execute()

        return {
            "report_id": report_id,
            "file_name": file_name,
            "download_url": f"/report/{analysis_id}/download/{file_name}",
        }
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")


@router.get("/{analysis_id}/download/{file_name}")
async def download_report(
    analysis_id: str,
    file_name: str,
    current_user: dict = Depends(get_current_user),
):
    """Download a generated PDF report."""
    file_path = os.path.join(REPORTS_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_name,
    )
