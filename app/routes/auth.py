
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import get_current_user
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.services.auth_service import register_user, login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest):

    try:
        result = register_user(
            full_name=data.full_name,
            email=data.email,
            password=data.password
        )

        return {
            "message": "Registration successful. Check your email if verification is required.",
            **result
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Registration failed. Check your input and Supabase Auth configuration."
        )


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(data: LoginRequest):

    try:
        result = login_user(
            email=data.email,
            password=data.password
        )

        return {
            "message": "Login successful",
            **result
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password, or email not verified."
        )


@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "message": "Authenticated successfully"
    }
