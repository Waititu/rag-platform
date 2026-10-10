from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document, DocumentChunk
from app.ingestion.service import IngestionService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        data = await file.read()

        document = IngestionService.ingest(
            db=db,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )

        return {
            "id": str(document.id),
            "filename": document.filename,
            "content_type": document.content_type,
            "size_bytes": document.size_bytes,
            "created_at": document.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(document.id),
            "filename": document.filename,
            "content_type": document.content_type,
            "size_bytes": document.size_bytes,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "id": str(document.id),
        "filename": document.filename,
        "content_type": document.content_type,
        "size_bytes": document.size_bytes,
        "text": document.text,
        "created_at": document.created_at,
    }


@router.get("/{document_id}/chunks")
def list_document_chunks(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    return [
        {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
        }
        for chunk in chunks
    ]

