from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ChatMessage, Conversation
from app.generation.service import GenerationService
from app.retrieval.service import RetrievalService


class ChatService:
    @staticmethod
    def create_conversation(
        db: Session,
        title: str = "New conversation",
    ) -> Conversation:
        conversation = Conversation(
            title=title.strip() or "New conversation"
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: UUID,
    ) -> Conversation | None:
        return db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )

    @staticmethod
    def list_conversations(
        db: Session,
    ) -> list[Conversation]:
        return list(
            db.scalars(
                select(Conversation).order_by(
                    Conversation.updated_at.desc()
                )
            ).all()
        )

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: UUID,
    ) -> list[ChatMessage]:
        return list(
            db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.conversation_id == conversation_id
                )
                .order_by(ChatMessage.created_at)
            ).all()
        )

    @staticmethod
    def send_message(
        db: Session,
        conversation: Conversation,
        content: str,
        top_k: int = 5,
    ) -> dict:
        content = content.strip()

        if not content:
            raise ValueError("Message cannot be empty")

        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=content,
        )

        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        history = ChatService.get_messages(
            db,
            conversation.id,
        )

        history_context = ChatService._build_history(
            history[:-1]
        )

        question = content

        if history_context:
            question = (
                f"Conversation history:\n"
                f"{history_context}\n\n"
                f"Current user question:\n"
                f"{content}"
            )

        result = ChatService._generate_rag_answer(
            db=db,
            question=question,
            top_k=top_k,
        )

        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
        )

        db.add(assistant_message)

        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(assistant_message)

        return {
            "conversation_id": str(conversation.id),
            "message": {
                "id": str(assistant_message.id),
                "role": "assistant",
                "content": assistant_message.content,
                "created_at": assistant_message.created_at,
            },
            "sources": result["sources"],
        }

    @staticmethod
    def stream_message(
        db: Session,
        conversation: Conversation,
        content: str,
        top_k: int = 5,
    ):
        content = content.strip()

        if not content:
            raise ValueError("Message cannot be empty")

        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=content,
        )

        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        history = ChatService.get_messages(
            db,
            conversation.id,
        )

        history_context = ChatService._build_history(
            history[:-1]
        )

        question = content

        if history_context:
            question = (
                f"Conversation history:\n"
                f"{history_context}\n\n"
                f"Current user question:\n"
                f"{content}"
            )

        results = RetrievalService.search(
            db=db,
            query=question,
            top_k=top_k,
        )

        if not results:
            answer = (
                "The available documents do not contain enough "
                "information to answer this question."
            )

            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
            )

            db.add(assistant_message)

            conversation.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(assistant_message)

            yield {
                "type": "token",
                "content": answer,
            }

            yield {
                "type": "done",
                "conversation_id": str(conversation.id),
                "message_id": str(assistant_message.id),
                "sources": [],
            }

            return

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

        context_parts = []

        for index, result in enumerate(results, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"Document: {result['filename']}\n"
                f"Chunk: {result['chunk_index']}\n"
                f"Content:\n{result['text']}"
            )

        context = "\n\n".join(context_parts)

        yield {
            "type": "sources",
            "sources": sources,
        }

        answer_parts = []

        for token in GenerationService.stream(
            question=question,
            context=context,
        ):
            answer_parts.append(token)

            yield {
                "type": "token",
                "content": token,
            }

        answer = "".join(answer_parts).strip()

        if not answer:
            raise ValueError(
                "Ollama returned no generated answer"
            )

        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )

        db.add(assistant_message)

        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(assistant_message)

        yield {
            "type": "done",
            "conversation_id": str(conversation.id),
            "message_id": str(assistant_message.id),
        }

    @staticmethod
    def _generate_rag_answer(
        db: Session,
        question: str,
        top_k: int,
    ) -> dict:
        results = RetrievalService.search(
            db=db,
            query=question,
            top_k=top_k,
        )

        if not results:
            return {
                "answer": (
                    "The available documents do not contain enough "
                    "information to answer this question."
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
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    def _build_history(
        messages: list[ChatMessage],
    ) -> str:
        if not messages:
            return ""

        return "\n".join(
            f"{message.role}: {message.content}"
            for message in messages
        )
