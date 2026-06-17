from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class CompoundBase(BaseModel):
    id: int
    formula: str
    name: str
    name_sr: Optional[str] = None
    composition: Dict[str, int]
    confidence_level: str
    school_level: Optional[str] = None
    state_at_stp: Optional[str] = None
    color: Optional[str] = None
    molar_mass: Optional[float] = None
    tags: Optional[List[str]] = None


class CompoundDetail(CompoundBase):
    description: Optional[str] = None
    uses: Optional[str] = None
    structure_description: Optional[str] = None
    melting_point_k: Optional[float] = None
    boiling_point_k: Optional[float] = None
    confidence_source: Optional[str] = None
    wikipedia_url: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None


class CompoundImage(BaseModel):
    id: int
    url: str
    caption: Optional[str] = None
    image_type: Optional[str] = None
