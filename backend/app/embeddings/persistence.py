from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.embeddings.service import EmbeddingService


class EmbeddingPersistenceService:

    @staticmethod
    def embed_chunks(
        db: Session,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        for chunk in chunks:
            chunk.embedding = EmbeddingService.embed(
                chunk.text
            )

        db.commit()

        for chunk in chunks:
            db.refresh(chunk)

        return chunks
