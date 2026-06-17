"""
Compound repository — native SQL queries using psycopg2.
"""
from typing import List, Optional
from app.db.connection import get_cursor


SELECT_BY_ID = """
SELECT
    c.id, c.formula, c.name, c.name_sr, c.composition,
    c.description, c.uses, c.structure_description,
    c.state_at_stp, c.color, c.melting_point_k, c.boiling_point_k, c.molar_mass,
    c.school_level,
    c.confidence_level, c.confidence_source,
    c.wikipedia_url, c.image_url, c.tags,
    COALESCE(
        array_agg(ci.url ORDER BY ci.id) FILTER (WHERE ci.url IS NOT NULL),
        ARRAY[]::TEXT[]
    ) AS images
FROM compounds c
LEFT JOIN compound_images ci ON ci.compound_id = c.id
WHERE c.id = %(id)s
GROUP BY c.id;
"""

SELECT_BY_FORMULA = """
SELECT
    c.id, c.formula, c.name, c.name_sr, c.composition,
    c.description, c.uses, c.structure_description,
    c.state_at_stp, c.color, c.melting_point_k, c.boiling_point_k, c.molar_mass,
    c.school_level,
    c.confidence_level, c.confidence_source,
    c.wikipedia_url, c.image_url, c.tags,
    COALESCE(
        array_agg(ci.url ORDER BY ci.id) FILTER (WHERE ci.url IS NOT NULL),
        ARRAY[]::TEXT[]
    ) AS images
FROM compounds c
LEFT JOIN compound_images ci ON ci.compound_id = c.id
WHERE c.formula = %(formula)s
GROUP BY c.id;
"""

SEARCH = """
SELECT
    id, formula, name, name_sr, composition,
    confidence_level, school_level, state_at_stp, color, molar_mass, tags
FROM compounds
WHERE
    (%(q)s IS NULL OR
     formula ILIKE %(pattern)s OR
     name ILIKE %(pattern)s OR
     name_sr ILIKE %(pattern)s)
    AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s)
ORDER BY
    CASE WHEN formula = %(q)s THEN 0 ELSE 1 END,
    name
LIMIT %(limit)s
OFFSET %(offset)s;
"""

COUNT_SEARCH = """
SELECT COUNT(*) AS total
FROM compounds
WHERE
    (%(q)s IS NULL OR
     formula ILIKE %(pattern)s OR
     name ILIKE %(pattern)s OR
     name_sr ILIKE %(pattern)s)
    AND (%(confidence)s IS NULL OR confidence_level = %(confidence)s);
"""


def get_by_id(compound_id: int) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(SELECT_BY_ID, {"id": compound_id})
        row = cur.fetchone()
        return dict(row) if row else None


def get_by_formula(formula: str) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(SELECT_BY_FORMULA, {"formula": formula})
        row = cur.fetchone()
        return dict(row) if row else None


def search(
    q: Optional[str] = None,
    confidence: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    pattern = f"%{q}%" if q else None
    params = {"q": q, "pattern": pattern, "confidence": confidence, "limit": limit, "offset": offset}

    with get_cursor() as cur:
        cur.execute(SEARCH, params)
        items = [dict(r) for r in cur.fetchall()]
        cur.execute(COUNT_SEARCH, params)
        total = cur.fetchone()["total"]
        return {"items": items, "total": total, "limit": limit, "offset": offset}

