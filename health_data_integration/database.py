"""
database.py
-----------
Handles SQLite storage for the unified health record store.

Every data source adapter normalizes its raw data into a common
"health_record" shape before it is saved here, so the rest of the
application never needs to know where a data point originally came from.
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "health_data.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS health_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    source TEXT NOT NULL,          -- e.g. 'wearable', 'manual', 'lab'
    metric TEXT NOT NULL,          -- e.g. 'heart_rate', 'weight_kg'
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    recorded_at TEXT NOT NULL,     -- ISO 8601 timestamp
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def get_or_create_patient(name: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("SELECT id FROM patients WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur = conn.execute("INSERT INTO patients (name) VALUES (?)", (name,))
        return cur.lastrowid


def insert_records(patient_id: int, records: list[dict]):
    """records: list of normalized health record dicts."""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO health_records
                (patient_id, source, metric, value, unit, recorded_at)
            VALUES (:patient_id, :source, :metric, :value, :unit, :recorded_at)
            """,
            [{**r, "patient_id": patient_id} for r in records],
        )


def get_records_for_patient(patient_id: int) -> list[dict]:
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT source, metric, value, unit, recorded_at
            FROM health_records
            WHERE patient_id = ?
            ORDER BY recorded_at ASC
            """,
            (patient_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def list_patients() -> list[dict]:
    with get_connection() as conn:
        cur = conn.execute("SELECT id, name FROM patients ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
