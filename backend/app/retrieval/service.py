from sqlalchemy import select

from app.db.models import Document, DocumentChunk
from app.embeddings.service import EmbeddingService
from app.retrieval.config import RetrievalConfig


class RetrievalService:
    def __init__(
        self,
        session,
        embedding_service: EmbeddingService | None = None,
        config: RetrievalConfig | None = None,
    ):
        self.session = session
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )
        self.config = config or RetrievalConfig()

    def search(
        self,
        query: str,
        top_k: int | None = None,
        min_similarity: float | None = None,
    ) -> list[dict]:
        query = self._validate_query(query)

        top_k = (
            self.config.default_top_k
            if top_k is None
            else top_k
        )

        self._validate_top_k(top_k)

        threshold = (
            self.config.min_similarity
            if min_similarity is None
            else min_similarity
        )

        self._validate_similarity_threshold(threshold)

        query_embedding = (
            self.embedding_service.embed(query)
        )

        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                distance.label("distance"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
            .order_by(distance.asc())
            .limit(
                min(
                    top_k * self.config.candidate_multiplier,
                    self.config.candidate_limit,
                )
            )
        )

        rows = self.session.execute(statement).all()

        results = []

        for chunk, filename, raw_distance in rows:
            similarity = 1.0 - float(raw_distance)

            if similarity < threshold:
                continue

            results.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "filename": filename,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "distance": float(raw_distance),
                    "similarity": similarity,
                }
            )

            if len(results) >= top_k:
                break

        return results

    @staticmethod
    def _validate_query(query: str) -> str:
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        return query

    def _validate_top_k(self, top_k: int) -> None:
        if not isinstance(top_k, int):
            raise ValueError("top_k must be an integer.")

        if not 1 <= top_k <= self.config.max_top_k:
            raise ValueError(
                f"top_k must be between 1 and "
                f"{self.config.max_top_k}."
            )

    @staticmethod
    def _validate_similarity_threshold(
        threshold: float,
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "min_similarity must be between 0 and 1."
            )
