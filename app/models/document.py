
import uuid

from sqlalchemy import (
    Column,
    Text,
    BigInteger,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    title = Column(Text, nullable=False)
    document_type = Column(Text, nullable=False)

    file_name = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(Text)
    file_size = Column(BigInteger)

    extracted_data = Column(
        JSONB,
        nullable=False,
        default=dict
    )
    processing_status = Column(
    Text,
    nullable=False,
    default="pending",
    server_default="pending"
    )


    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


processing_status = Column(
    Text,
    nullable=False,
    default="pending",
    server_default="pending"
)
