
from app.core.supabase_client import get_supabase_client


def register_user(full_name: str, email: str, password: str):
    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "full_name": full_name
            }
        }
    })

    if not response.user:
        raise ValueError("Unable to create user account")

    return {
        "user_id": str(response.user.id),
        "email": response.user.email,
        "email_confirmation_required": response.session is None
    }


def login_user(email: str, password: str):
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not response.user or not response.session:
        raise ValueError("Login failed")

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user_id": str(response.user.id),
        "email": response.user.email
    }
