"""Supabase database client initialization"""
from supabase import create_client, Client
from backend.core.config import settings


def get_supabase_client(use_service_key: bool = False) -> Client:
    """
    Create and return a Supabase client instance
    
    Args:
        use_service_key: If True, uses service role key (bypasses RLS).
                        If False, uses anon key (respects RLS).
    
    Returns:
        Supabase Client instance
    """
    key = settings.supabase_service_key if use_service_key else settings.supabase_anon_key
    
    client: Client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=key
    )
    
    return client


# Dependency for FastAPI endpoints
def get_supabase() -> Client:
    """FastAPI dependency to get Supabase client with anon key"""
    return get_supabase_client(use_service_key=False)


def get_supabase_admin() -> Client:
    """Get Supabase client with service role key (for admin operations)"""
    return get_supabase_client(use_service_key=True)

