"""
Supabase Client - Database connection and initialization
"""

from typing import Any

import httpx
from supabase import create_client, Client
from loguru import logger
from backend.config import settings


class _CompatSyncClient(httpx.Client):
    def __init__(self, *args: Any, proxy: str | None = None, **kwargs: Any) -> None:
        kwargs.pop("proxy", None)
        super().__init__(*args, **kwargs)


def _patch_gotrue_http_client() -> None:
    import gotrue._sync.gotrue_base_api as gotrue_base_api
    import gotrue._sync.gotrue_admin_api as gotrue_admin_api
    import gotrue._sync.gotrue_client as gotrue_client
    import gotrue.http_clients as gotrue_http_clients

    gotrue_http_clients.SyncClient = _CompatSyncClient
    gotrue_base_api.SyncClient = _CompatSyncClient
    gotrue_admin_api.SyncClient = _CompatSyncClient
    gotrue_client.SyncClient = _CompatSyncClient

_supabase_client: Client | None = None


def init_supabase() -> Client:
    """Initialize and return Supabase client."""
    global _supabase_client
    try:
        _patch_gotrue_http_client()
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )
        logger.info("✅ Supabase client initialized")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Supabase init failed: {e}")
        raise


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        return init_supabase()
    return _supabase_client


def get_admin_supabase() -> Client:
    """Get admin Supabase client with service role key (bypasses RLS)."""
    _patch_gotrue_http_client()
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY,
    )
