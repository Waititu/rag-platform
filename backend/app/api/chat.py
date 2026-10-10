import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.chat import ChatService
from app.db.database import get_db


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class CreateConversationRequest(BaseModel):
    title: str = Field(
        default="New conversation",
        min_length=1,
        max_length=255,
    )


class SendMessageRequest(BaseModel):
    content: str = Field(
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


@router.post("/conversations")
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
):
    conversation = ChatService.create_conversation(
        db=db,
        title=request.title,
    )

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
):
    conversations = ChatService.list_conversations(db)

    return [
        {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
):
    conversation = ChatService.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = ChatService.get_messages(
        db=db,
        conversation_id=conversation.id,
    )

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
):
    conversation = ChatService.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = ChatService.get_messages(
        db=db,
        conversation_id=conversation_id,
    )

    return [
        {
            "id": str(message.id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
):
    conversation = ChatService.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    try:
        return ChatService.send_message(
            db=db,
            conversation=conversation,
            content=request.content,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/conversations/{conversation_id}/messages/stream"
)
def stream_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
):
    conversation = ChatService.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    def event_stream():
        try:
            for event in ChatService.stream_message(
                db=db,
                conversation=conversation,
                content=request.content,
                top_k=request.top_k,
            ):
                yield (
                    f"data: "
                    f"{json.dumps(event, default=str)}"
                    f"\n\n"
                )

            yield "data: [DONE]\n\n"

        except Exception as exc:
            db.rollback()

            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "error",
                        "error": str(exc),
                    }
                )
                + "\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
