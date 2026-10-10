from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.rag import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


class RAGRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("")
def answer_question(
    request: RAGRequest,
    db: Session = Depends(get_db),
):
    try:
        return RAGService.answer(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
