"""
History Routes - Retrieve past analyses
"""

from fastapi import APIRouter, Depends, Query
from backend.auth.jwt_handler import get_current_user
from backend.database.supabase_client import get_supabase

router = APIRouter()


@router.get("/")
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """Get analysis history for the current user."""
    supabase = get_supabase()
    result = (
        supabase.table("analyses")
        .select(
            "id, job_title, company_name, ats_score, semantic_similarity, "
            "keyword_match_pct, skill_overlap_pct, status, created_at"
        )
        .eq("user_id", current_user["id"])
        .eq("status", "completed")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    data = result.data or []
    return {
        "analyses": data,
        "total": len(data),
        "limit": limit,
        "offset": offset,
    }


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an analysis from history."""
    supabase = get_supabase()
    supabase.table("analyses").delete().eq("id", analysis_id).eq("user_id", current_user["id"]).execute()
    return {"message": "Analysis deleted"}
