
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=30)
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    additional_info: Optional[dict] = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    additional_info: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
