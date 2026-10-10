from sqlalchemy.orm import Session

from app.chunking.persistence import ChunkPersistenceService
from app.chunking.service import ChunkingService
from app.db.models import Document
from app.embeddings.persistence import EmbeddingPersistenceService
from app.ingestion.parser import DocumentParser


class IngestionService:

    @staticmethod
    def ingest(
        db: Session,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Document:

        text = DocumentParser.parse(
            filename=filename,
            content_type=content_type,
            data=data,
        )

        if not text.strip():
            raise ValueError(
                "Document contains no extractable text"
            )

        document = Document(
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            text=text,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        chunker = ChunkingService(
            chunk_size=1000,
            chunk_overlap=200,
        )

        chunks = chunker.chunk(document.text)

        records = ChunkPersistenceService.save_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        EmbeddingPersistenceService.embed_chunks(
            db=db,
            chunks=records,
        )

        return document

