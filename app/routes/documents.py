
import uuid
from pathlib import Path
from uuid import UUID
from sqlalchemy import text
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas.document import DocumentUpdateRequest
from app.core.security import get_current_user
from app.core.supabase_client import get_supabase_storage_client
from app.database.connection import get_db
from app.models.document import Document

router = APIRouter(prefix="/documents", tags=["Documents"])

BUCKET_NAME = "documents"
MAX_FILE_SIZE = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".docx"
}


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate filename and extension
    original_filename = Path(file.filename or "").name

    if not original_filename:
        raise HTTPException(400, "Invalid filename")

    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            "Unsupported file format"
        )

    # 2. Read and validate file size
    file_content = file.file.read(MAX_FILE_SIZE + 1)

    if not file_content:
        raise HTTPException(400, "Empty file")

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            "File size exceeds the 50 MB limit"
        )

    # 3. Generate a unique storage path
    user_id = str(current_user.id)
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = f"{user_id}/{unique_filename}"

    content_type = (
        file.content_type or "application/octet-stream"
    )

    storage = get_supabase_storage_client()

    # 4. Upload file to Supabase Storage
    try:
        storage.storage.from_(BUCKET_NAME).upload(
            file_path,
            file_content,
            file_options={
                "content-type": content_type,
                "upsert": "false"
            }
        )
    except Exception as exc:
        db.rollback()
        print("DATABASE SAVE ERROR:", repr(exc))
        raise HTTPException(
            status_code=500,
            detail="Failed to save document information"
    )

    # 5. Save document metadata in PostgreSQL
    try:
        document = Document(
            user_id=current_user.id,
            title=title or Path(original_filename).stem,
            document_type=document_type,
            file_name=original_filename,
            file_path=file_path,
            file_type=content_type,
            file_size=len(file_content),
            description=description,
            extracted_data={}
        )

        db.add(document)
        db.commit()
        db.refresh(document)


    except Exception as exc:
        import traceback

        db.rollback()

        print("DATABASE SAVE ERROR:", repr(exc))
        traceback.print_exc()

        # Remove uploaded file if database insertion fails
        try:
            storage.storage.from_(BUCKET_NAME).remove(
                [file_path]
            )
        except Exception as storage_exc:
            print("STORAGE CLEANUP ERROR:", repr(storage_exc))

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document information: {str(exc)}"
        )

    return {
        "message": "Document uploaded successfully",
        "document_id": str(document.id),
        "file_name": document.file_name,
        "document_type": document.document_type,
        "file_path": document.file_path,
        "file_size": document.file_size
    }


# GET ALL DOCUMENTS OF LOGGED-IN USER
@router.get("/")
def get_documents(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        query = text("""
            SELECT
                id,
                title,
                document_type,
                file_name,
                file_path,
                file_type,
                file_size,
                extracted_data,
                description,
                created_at,
                updated_at
            FROM public.documents
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)

        result = db.execute(
            query,
            {"user_id": str(current_user.id)}
        )

        documents = [dict(row) for row in result.mappings().all()]

        return {
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as exc:
        print("GET DOCUMENTS ERROR:", repr(exc))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve documents"
        )


# GET ONE DOCUMENT BY ID
@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        query = text("""
            SELECT
                id,
                title,
                document_type,
                file_name,
                file_path,
                file_type,
                file_size,
                extracted_data,
                description,
                created_at,
                updated_at
            FROM public.documents
            WHERE id = :document_id
            AND user_id = :user_id
        """)

        result = db.execute(
            query,
            {
                "document_id": str(document_id),
                "user_id": str(current_user.id)
            }
        )

        document = result.mappings().first()

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        return dict(document)

    except HTTPException:
        raise

    except Exception as exc:
        print("GET DOCUMENT ERROR:", repr(exc))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document"
        )


@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. Find document and verify ownership
        query = text("""
            SELECT id, file_path
            FROM public.documents
            WHERE id = :document_id
            AND user_id = :user_id
        """)

        result = db.execute(
            query,
            {
                "document_id": str(document_id),
                "user_id": str(current_user.id)
            }
        )

        document = result.mappings().first()

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        # 2. Delete actual file from Supabase Storage
        storage = get_supabase_storage_client()

        try:
            storage.storage.from_(BUCKET_NAME).remove(
                [document["file_path"]]
            )
        except Exception as storage_exc:
            print("STORAGE DELETE ERROR:", repr(storage_exc))

            raise HTTPException(
                status_code=500,
                detail="Failed to delete document file from storage"
            )

        # 3. Delete database record
        delete_query = text("""
            DELETE FROM public.documents
            WHERE id = :document_id
            AND user_id = :user_id
        """)

        db.execute(
            delete_query,
            {
                "document_id": str(document_id),
                "user_id": str(current_user.id)
            }
        )

        db.commit()

        return {
            "message": "Document deleted successfully",
            "document_id": str(document_id)
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        print("DELETE DOCUMENT ERROR:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )


@router.put("/{document_id}")
def update_document(
    document_id: UUID,
    request: DocumentUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. Find document and verify ownership
        check_query = text("""
            SELECT id
            FROM public.documents
            WHERE id = :document_id
            AND user_id = :user_id
        """)

        existing = db.execute(
            check_query,
            {
                "document_id": str(document_id),
                "user_id": str(current_user.id)
            }
        ).first()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        # 2. Get only fields supplied by the user
        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        # 3. Build safe update query
        allowed_fields = {"title", "document_type", "description"}

        update_data = {
            key: value
            for key, value in update_data.items()
            if key in allowed_fields
        }

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No valid fields provided"
            )

        update_data["document_id"] = str(document_id)
        update_data["user_id"] = str(current_user.id)

        set_clause = ", ".join(
            f"{key} = :{key}" for key in update_data
            if key not in {"document_id", "user_id"}
        )

        update_query = text(f"""
            UPDATE public.documents
            SET {set_clause},
                updated_at = NOW()
            WHERE id = :document_id
            AND user_id = :user_id
            RETURNING *
        """)

        result = db.execute(update_query, update_data)
        updated_document = result.mappings().first()

        db.commit()

        return {
            "message": "Document updated successfully",
            "document": dict(updated_document)
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        print("UPDATE DOCUMENT ERROR:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail="Failed to update document"
        )
