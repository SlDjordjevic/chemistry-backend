"""
Reaction repository — the core wizard SQL queries.

All queries use PostgreSQL JSONB @> containment operator backed by GIN index.

Key queries:
1. get_compatible_elements(partial_composition)
   → Which elements appear in compounds that CONTAIN partial_composition as a subset?

2. get_atom_counts_with_previews(partial_composition, element)
   → For each possible atom count of `element` in compounds containing partial_composition,
     return the list of compounds (with formula and name) that match.
     Marks each compound as `is_complete` (composition exactly matches partial + {element: n})
     or not (compound contains more elements → can continue extending).

3. get_next_elements(composition)
   → Alias of get_compatible_elements — used after user locks in a count to find next options.
"""
import json
from typing import Dict, List, Optional
from psycopg2.extras import Json
from app.db.connection import get_cursor


# Query 1: Compatible elements
# Finds all element keys present in compounds that contain @> partial_composition
GET_COMPATIBLE_ELEMENTS = """
WITH matching AS (
    SELECT composition
    FROM compounds
    WHERE composition @> %(partial)s::jsonb
      AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s)
)
SELECT DISTINCT jsonb_object_keys(composition) AS element
FROM matching
WHERE jsonb_object_keys NOT IN (
    SELECT jsonb_object_keys(%(partial)s::jsonb)
)
ORDER BY element;
"""

# Cleaner version using a subquery to exclude already-selected elements
GET_COMPATIBLE_ELEMENTS_V2 = """
SELECT DISTINCT key AS element
FROM compounds,
     jsonb_each(composition) AS kv(key, val)
WHERE composition @> %(partial)s::jsonb
  AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s)
  AND key NOT IN (
      SELECT jsonb_object_keys(%(partial)s::jsonb)
  )
ORDER BY element;
"""

# Query 2: Atom counts with compound previews
# For a given element, find all atom counts in compounds that contain partial_composition
GET_ATOM_COUNTS_WITH_PREVIEWS = """
SELECT
    (composition->>%(element)s)::int  AS atom_count,
    id,
    formula,
    name,
    name_sr,
    confidence_level,
    molar_mass,
    -- is_complete: composition has EXACTLY the same number of keys
    --   as partial_composition + 1 (for the new element),
    --   meaning no more elements can be added.
    (jsonb_typeof(composition) = 'object'
     AND (
       SELECT count(*) FROM jsonb_object_keys(composition)
     ) = (
       SELECT count(*) FROM jsonb_object_keys(%(partial)s::jsonb)
     ) + 1
    ) AS is_complete
FROM compounds
WHERE composition @> %(partial)s::jsonb
  AND composition ? %(element)s
  AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s)
ORDER BY atom_count, formula;
"""

# Query 3: Resolve — find compounds with EXACT composition
GET_EXACT_COMPOUNDS = """
SELECT
    id, formula, name, name_sr,
    confidence_level, molar_mass,
    TRUE AS is_complete
FROM compounds
WHERE composition = %(composition)s::jsonb
  AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s)
ORDER BY formula;
"""


def _jsonb_str(d: Dict) -> str:
    return json.dumps(d, sort_keys=True)


def get_compatible_elements(
    partial_composition: Dict[str, int],
    confidence: Optional[str] = None,
) -> List[str]:
    """Returns a sorted list of element symbols that can be added to partial_composition."""
    params = {
        "partial": _jsonb_str(partial_composition),
        "confidence": confidence,
    }
    with get_cursor() as cur:
        cur.execute(GET_COMPATIBLE_ELEMENTS_V2, params)
        return [row["element"] for row in cur.fetchall()]


def get_atom_counts_with_previews(
    partial_composition: Dict[str, int],
    element: str,
    confidence: Optional[str] = None,
) -> List[dict]:
    """
    Returns a list grouped by atom_count, each with a list of matching compound previews.
    Example return value:
    [
      {"count": 1, "compounds": [{"id": 1, "formula": "CH4", "name": "Methane", ...}]},
      {"count": 2, "compounds": [...]},
    ]
    """
    params = {
        "partial": _jsonb_str(partial_composition),
        "element": element,
        "confidence": confidence,
    }
    with get_cursor() as cur:
        cur.execute(GET_ATOM_COUNTS_WITH_PREVIEWS, params)
        rows = cur.fetchall()

    # Group by atom_count
    from collections import defaultdict
    groups: Dict[int, list] = defaultdict(list)
    for row in rows:
        count = row["atom_count"]
        groups[count].append({
            "id": row["id"],
            "formula": row["formula"],
            "name": row["name"],
            "name_sr": row["name_sr"],
            "confidence_level": row["confidence_level"],
            "molar_mass": row["molar_mass"],
            "is_complete": row["is_complete"],
        })

    return [
        {"count": count, "compounds": compounds}
        for count, compounds in sorted(groups.items())
    ]


def get_exact_compounds(
    composition: Dict[str, int],
    confidence: Optional[str] = None,
) -> List[dict]:
    """Finds compounds where composition exactly matches the given dict."""
    params = {
        "composition": _jsonb_str(composition),
        "confidence": confidence,
    }
    with get_cursor() as cur:
        cur.execute(GET_EXACT_COMPOUNDS, params)
        return [dict(row) for row in cur.fetchall()]

