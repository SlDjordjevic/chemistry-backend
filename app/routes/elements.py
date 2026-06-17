from fastapi import APIRouter, HTTPException
from app.repositories import element_repo
from app.schemas.element import ElementBase, ElementDetail

router = APIRouter()


@router.get("", response_model=list[ElementBase])
def list_elements():
    """Return all elements — used to render the periodic table."""
    return element_repo.get_all()


@router.get("/{symbol}", response_model=ElementDetail)
def get_element(symbol: str):
    """Return full details for a single element by symbol."""
    el = element_repo.get_by_symbol(symbol.upper())
    if not el:
        raise HTTPException(status_code=404, detail=f"Element '{symbol}' not found")
    return el

