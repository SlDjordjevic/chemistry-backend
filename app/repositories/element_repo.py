"""
Element repository — native SQL queries using psycopg2.
"""
from typing import List, Optional
from app.db.connection import get_cursor


SELECT_ALL = """
SELECT
    id, atomic_number, symbol, name, name_sr,
    atomic_weight, "group", period, category,
    protons, electrons, neutrons,
    electron_shells, electron_configuration, valence_electrons,
    oxidation_states, electronegativity, atomic_radius_pm,
    melting_point_k, boiling_point_k, density_g_cm3,
    state_at_stp, occurrence, description, properties,
    wikipedia_url, color_hex, grid_row, grid_col
FROM elements
ORDER BY atomic_number;
"""

SELECT_BY_SYMBOL = """
SELECT
    id, atomic_number, symbol, name, name_sr,
    atomic_weight, "group", period, category,
    protons, electrons, neutrons,
    electron_shells, electron_configuration, valence_electrons,
    oxidation_states, electronegativity, atomic_radius_pm,
    melting_point_k, boiling_point_k, density_g_cm3,
    state_at_stp, occurrence, description, properties,
    wikipedia_url, color_hex, grid_row, grid_col
FROM elements
WHERE symbol = %(symbol)s;
"""

SELECT_BY_ATOMIC_NUMBER = """
SELECT
    id, atomic_number, symbol, name, name_sr,
    atomic_weight, "group", period, category,
    protons, electrons, neutrons,
    electron_shells, electron_configuration, valence_electrons,
    oxidation_states, electronegativity, atomic_radius_pm,
    melting_point_k, boiling_point_k, density_g_cm3,
    state_at_stp, occurrence, description, properties,
    wikipedia_url, color_hex, grid_row, grid_col
FROM elements
WHERE atomic_number = %(atomic_number)s;
"""

SELECT_BY_SYMBOLS = """
SELECT symbol, name, name_sr, color_hex, category, grid_row, grid_col, period, "group"
FROM elements
WHERE symbol = ANY(%(symbols)s)
ORDER BY atomic_number;
"""


def _normalize_symbol(symbol: str) -> str:
    """Normalize chemical symbol casing: sn -> Sn, AR -> Ar, h -> H."""
    symbol = (symbol or "").strip()
    if not symbol:
        return symbol
    return symbol[:1].upper() + symbol[1:].lower()


def get_all() -> List[dict]:
    with get_cursor() as cur:
        cur.execute(SELECT_ALL)
        return [dict(r) for r in cur.fetchall()]


def get_by_symbol(symbol: str) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(SELECT_BY_SYMBOL, {"symbol": _normalize_symbol(symbol)})
        row = cur.fetchone()
        return dict(row) if row else None


def get_by_atomic_number(atomic_number: int) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(SELECT_BY_ATOMIC_NUMBER, {"atomic_number": atomic_number})
        row = cur.fetchone()
        return dict(row) if row else None


def get_by_symbols(symbols: List[str]) -> List[dict]:
    if not symbols:
        return []
    with get_cursor() as cur:
        cur.execute(SELECT_BY_SYMBOLS, {"symbols": symbols})
        return [dict(r) for r in cur.fetchall()]
