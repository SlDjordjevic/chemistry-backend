from typing import Optional, List, Any
from pydantic import BaseModel


class ElementBase(BaseModel):
    atomic_number: int
    symbol: str
    name: str
    name_sr: str
    category: str
    period: int
    group: Optional[int] = None
    color_hex: str
    grid_row: int
    grid_col: int


class ElementDetail(ElementBase):
    atomic_weight: Optional[float] = None
    protons: int
    electrons: int
    neutrons: Optional[int] = None
    electron_shells: List[int]
    electron_configuration: Optional[str] = None
    valence_electrons: Optional[int] = None
    oxidation_states: Optional[List[str]] = None
    electronegativity: Optional[float] = None
    atomic_radius_pm: Optional[int] = None
    melting_point_k: Optional[float] = None
    boiling_point_k: Optional[float] = None
    density_g_cm3: Optional[float] = None
    state_at_stp: str
    occurrence: str
    description: Optional[str] = None
    properties: Optional[Any] = None
    wikipedia_url: Optional[str] = None

