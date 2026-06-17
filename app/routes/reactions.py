from fastapi import APIRouter
from app.repositories import reaction_repo
from app.schemas.reaction import (
    CompatibleElementsRequest, CompatibleElementsResponse,
    AtomCountsRequest, AtomCountsResponse,
    ResolveCompoundRequest, ResolveCompoundResponse,
)

router = APIRouter()


@router.post("/compatible-elements", response_model=CompatibleElementsResponse)
def compatible_elements(req: CompatibleElementsRequest):
    """
    Given a partial composition, return elements that can be combined with it.
    E.g. {"H": 4} → ["C", "N", "O", "Si", ...]
    """
    elements = reaction_repo.get_compatible_elements(
        req.composition, req.confidence_filter
    )
    return {"elements": elements}


@router.post("/atom-counts", response_model=AtomCountsResponse)
def atom_counts(req: AtomCountsRequest):
    """
    Given a partial composition and a next element, return all possible
    atom counts for that element with compound previews.
    E.g. composition={"H":4}, element="C"
    → [{count:1, compounds:[{CH4, Metan, ...}]}, {count:2, compounds:[{C2H4,...}]}]
    """
    options = reaction_repo.get_atom_counts_with_previews(
        req.composition, req.element, req.confidence_filter
    )
    return {"element": req.element, "options": options}


@router.post("/resolve", response_model=ResolveCompoundResponse)
def resolve_compound(req: ResolveCompoundRequest):
    """
    Find compound(s) that exactly match a given composition.
    Returns list of matches plus the first exact match (if any).
    """
    compounds = reaction_repo.get_exact_compounds(req.composition)
    previews = [
        {
            "id": c["id"],
            "formula": c["formula"],
            "name": c["name"],
            "name_sr": c.get("name_sr"),
            "confidence_level": c["confidence_level"],
            "molar_mass": c.get("molar_mass"),
            "is_complete": True,
        }
        for c in compounds
    ]
    return {
        "compounds": previews,
        "exact_match": previews[0] if previews else None,
    }

