from supabase import create_client
from app.core.config import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SECRET_KEY
)

BUCKET_NAME = "documents"


def get_storage():
    return supabase.storage.from_(BUCKET_NAME)