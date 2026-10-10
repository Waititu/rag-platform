from sqlalchemy.orm import Session

from app.generation.service import GenerationService
from app.retrieval.service import RetrievalService


class RAGService:

    @staticmethod
    def answer(
        db: Session,
        question: str,
        top_k: int = 5,
    ) -> dict:

        if not question.strip():
            raise ValueError("Question cannot be empty")

        service = RetrievalService(db)

        results = service.search(
            query=question,
            top_k=top_k,
        )

        if not results:
            return {
                "question": question,
                "answer": (
                    "I couldn't find sufficiently relevant "
                    "information in the indexed documents."
                ),
                "sources": [],
            }

        context_parts = []

        for index, result in enumerate(results, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"Document: {result['filename']}\n"
                f"Chunk: {result['chunk_index']}\n"
                f"Content:\n{result['text']}"
            )

        context = "\n\n".join(context_parts)

        answer = GenerationService.generate(
            question=question,
            context=context,
        )

        sources = [
            {
                "document_id": result["document_id"],
                "chunk_id": result["chunk_id"],
                "filename": result["filename"],
                "chunk_index": result["chunk_index"],
                "distance": result["distance"],
                "similarity": result["similarity"],
            }
            for result in results
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
