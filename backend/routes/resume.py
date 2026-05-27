"""
Resume Routes - Upload and parse resume files
"""

import uuid
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from loguru import logger

from backend.auth.jwt_handler import get_current_user
from backend.models.schemas import ResumeUploadResponse
from backend.services.file_parser import parse_resume_file, validate_file
from backend.nlp.nlp_pipeline import parse_resume
from backend.database.supabase_client import get_supabase, get_admin_supabase
from backend.config import settings

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload and parse a resume file (PDF/DOC/DOCX)."""
    try:
        content = await file.read()
        validate_file(content, file.filename, settings.MAX_FILE_SIZE_MB)

        # Extract text
        raw_text, page_count = parse_resume_file(content, file.filename)

        if len(raw_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Could not extract sufficient text from the resume. "
                       "Please ensure the file is not image-based.",
            )

        # Run NLP parsing
        parsed_data = parse_resume(raw_text)
        word_count = len(raw_text.split())
        resume_id = str(uuid.uuid4())

        # Save to Supabase (use admin client to bypass RLS for server-side inserts)
        supabase = get_supabase()
        admin = get_admin_supabase()
        record = {
            "id": resume_id,
            "user_id": current_user["id"],
            "file_name": file.filename,
            "raw_text": raw_text[:50000],  # limit storage
            "parsed_data": {
                "skills": parsed_data.get("skills", []),
                "keywords": parsed_data.get("keywords", []),
                "sections": parsed_data.get("sections", []),
                "contact_info": parsed_data.get("contact_info", {}),
                "section_completeness": parsed_data.get("section_completeness", 0),
            },
            "word_count": word_count,
            "page_count": page_count,
        }

        admin.table("resumes").insert(record).execute()
        logger.info(f"Resume uploaded: {resume_id} for user {current_user['id']}")

        return ResumeUploadResponse(
            resume_id=resume_id,
            file_name=file.filename,
            raw_text=raw_text,
            word_count=word_count,
            page_count=page_count,
            parsed_data=record["parsed_data"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get resume by ID."""
    supabase = get_supabase()
    result = (
        supabase.table("resumes")
        .select("*")
        .eq("id", resume_id)
        .eq("user_id", current_user["id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Resume not found")
    return result.data


@router.get("/")
async def list_resumes(current_user: dict = Depends(get_current_user)):
    """List all resumes for current user."""
    supabase = get_supabase()
    result = (
        supabase.table("resumes")
        .select("id, file_name, word_count, page_count, created_at")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    return {"resumes": result.data or [], "total": len(result.data or [])}
