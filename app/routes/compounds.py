from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.repositories import compound_repo
from app.schemas.compound import CompoundBase, CompoundDetail

router = APIRouter()


@router.get("/search")
def search_compounds(
    q: Optional[str] = Query(None),
    confidence: Optional[str] = Query(None, pattern="^(confirmed|theoretical)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Search compounds by formula/name with optional confidence filter."""
    return compound_repo.search(q=q, confidence=confidence, limit=limit, offset=offset)


@router.get("/{compound_id}", response_model=CompoundDetail)
def get_compound(compound_id: int):
    """Return full details for a compound by ID."""
    c = compound_repo.get_by_id(compound_id)
    if not c:
        raise HTTPException(status_code=404, detail="Compound not found")
    return c

