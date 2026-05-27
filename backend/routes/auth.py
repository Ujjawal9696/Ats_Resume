"""
Auth Routes - Signup, Login, Google OAuth, profile management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from loguru import logger
import httpx
import json

from backend.models.schemas import (
    SignupRequest, LoginRequest, TokenResponse, UserProfile
)
from backend.auth.jwt_handler import (
    create_access_token, hash_password, verify_password, get_current_user
)
from backend.database.supabase_client import get_supabase, get_admin_supabase
from backend.config import settings

router = APIRouter()


# ── Signup ────────────────────────────────────────────────────────────────────
@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: SignupRequest):
    supabase = get_supabase()
    try:
        # Register with Supabase Auth
        result = supabase.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {"full_name": body.full_name or ""}
            }
        })
        if not result.user:
            raise HTTPException(status_code=400, detail="Signup failed")

        user_id = result.user.id
        email = result.user.email

        # Upsert profile
        admin = get_admin_supabase()
        admin.table("profiles").upsert({
            "id": user_id,
            "email": email,
            "full_name": body.full_name or "",
        }).execute()

        token = create_access_token({"sub": user_id, "email": email})
        return TokenResponse(
            access_token=token,
            user={"id": user_id, "email": email, "full_name": body.full_name},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    supabase = get_supabase()
    try:
        result = supabase.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if not result.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = result.user.id
        email = result.user.email

        # Fetch profile
        profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        profile = profile_res.data or {}

        token = create_access_token({"sub": user_id, "email": email})
        return TokenResponse(access_token=token, user=profile or {"id": user_id, "email": email})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login():
    supabase = get_supabase()
    try:
        result = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": settings.GOOGLE_REDIRECT_URI},
        })
        return RedirectResponse(url=result.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth failed: {e}")


@router.get("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth callback and return JWT."""
    supabase = get_supabase()
    try:
        result = supabase.auth.exchange_code_for_session(code)
        if not result.user:
            raise HTTPException(status_code=401, detail="OAuth callback failed")

        user_id = result.user.id
        email = result.user.email
        full_name = result.user.user_metadata.get("full_name", "")
        avatar_url = result.user.user_metadata.get("avatar_url", "")

        # Upsert profile
        admin = get_admin_supabase()
        admin.table("profiles").upsert({
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url,
        }).execute()

        token = create_access_token({"sub": user_id, "email": email})
        redirect_url = f"{settings.FRONTEND_URL}?token={token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── Profile ───────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
