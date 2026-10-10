from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.chunking.service import Chunk


class ChunkPersistenceService:

    @staticmethod
    def save_chunks(
        db: Session,
        document_id,
        chunks: list[Chunk],
    ) -> list[DocumentChunk]:

        records = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=chunk.index,
                text=chunk.text,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
            )
            for chunk in chunks
        ]

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)

        return records
