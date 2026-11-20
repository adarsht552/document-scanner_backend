
from pydantic import BaseModel, Field
from typing import Optional


class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    document_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: Optional[str] = None
