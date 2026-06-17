import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "chemistry"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_SERVER", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        cursor_factory=RealDictCursor,
    )


@contextmanager
def get_cursor():
    """Context manager that yields a cursor and handles commit/rollback."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

