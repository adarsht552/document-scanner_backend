
from dataclasses import fields

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from app.core.security import get_current_user
from app.database.connection import get_db
from app.schemas.profile import ProfileUpdateRequest

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/me")
def get_my_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            id,
            email,
            full_name,
            phone,
            date_of_birth,
            address,
            additional_info,
            created_at,
            updated_at
        FROM public.profiles
        WHERE id = :user_id
    """)

    result = db.execute(
        query,
        {"user_id": str(current_user.id)}
    ).mappings().first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return dict(result)


@router.put("/me")
def update_my_profile(
    profile_data: ProfileUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = profile_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No profile fields provided"
        )

    allowed_fields = {
        "full_name",
        "phone",
        "date_of_birth",
        "address",
        "additional_info"
    }

    fields = [
        field for field in update_data
        if field in allowed_fields
    ]

    set_clause = ", ".join(
        f"{field} = :{field}" for field in fields
    )

    query = text(f"""
    UPDATE public.profiles
    SET {set_clause}, updated_at = NOW()
    WHERE id = :user_id
    RETURNING *
""")

    if "additional_info" in fields:
     query = query.bindparams(
        bindparam("additional_info", type_=JSONB)
    )

    update_data["user_id"] = str(current_user.id)

    result = db.execute(query, update_data).mappings().first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    db.commit()

    return dict(result)
