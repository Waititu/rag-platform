from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.retrieval.service import RetrievalService


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("")
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    try:
        service = RetrievalService(db)

        results = service.search(
            query=request.query,
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "count": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
