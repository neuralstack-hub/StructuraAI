
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

DATABASE_PATH = DATA_DIR / "structuraai.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                prediction TEXT NOT NULL,
                crack_probability REAL NOT NULL,
                confidence REAL NOT NULL,
                image_width INTEGER NOT NULL,
                image_height INTEGER NOT NULL,
                model_epoch INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()


def save_inspection(
    filename,
    prediction,
    crack_probability,
    confidence,
    image_width,
    image_height,
    model_epoch,
):
    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO inspections (
                filename,
                prediction,
                crack_probability,
                confidence,
                image_width,
                image_height,
                model_epoch,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                filename,
                prediction,
                crack_probability,
                confidence,
                image_width,
                image_height,
                model_epoch,
            )
        )

        connection.commit()

        return cursor.lastrowid


def get_inspections(limit=50):
    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM inspections
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(row) for row in rows]


def get_inspection(inspection_id):
    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM inspections
            WHERE id = ?
            """,
            (inspection_id,)
        ).fetchone()

        return dict(row) if row else None
