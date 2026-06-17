from typing import Dict, Optional, List
from pydantic import BaseModel


class CompatibleElementsRequest(BaseModel):
    """
    Given current partial composition, return compatible next elements.
    Example: {"H": 2} -> returns ["O", "Cl", "N", ...]
    """
    composition: Dict[str, int]
    confidence_filter: Optional[str] = None  # "confirmed", "theoretical", None=all


class CompatibleElementsResponse(BaseModel):
    elements: List[str]


class CompoundPreview(BaseModel):
    id: int
    formula: str
    name: str
    name_sr: Optional[str] = None
    confidence_level: str
    molar_mass: Optional[float] = None
    is_complete: bool  # True if composition exactly matches this compound


class AtomCountOption(BaseModel):
    count: int
    compounds: List[CompoundPreview]  # Compounds where this count completes or extends


class AtomCountsRequest(BaseModel):
    """
    Given partial composition and a next element to add,
    return all possible atom counts for that element and preview compounds.
    Example: composition={"H":4}, element="C"
    -> [{count:1, compounds:[{CH4, metan,...}]}, {count:2, compounds:[...]}]
    """
    composition: Dict[str, int]
    element: str
    confidence_filter: Optional[str] = None


class AtomCountsResponse(BaseModel):
    element: str
    options: List[AtomCountOption]


class ResolveCompoundRequest(BaseModel):
    """Final resolution — find exact compound for given complete composition."""
    composition: Dict[str, int]


class ResolveCompoundResponse(BaseModel):
    compounds: List[CompoundPreview]
    exact_match: Optional[CompoundPreview] = None

