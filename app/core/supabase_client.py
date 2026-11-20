
from supabase import create_client
from app.core.config import settings


def get_supabase_client():
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_PUBLISHABLE_KEY
    )

def get_supabase_storage_client():
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY
    )