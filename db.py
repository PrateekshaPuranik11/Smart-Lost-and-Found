"""
db.py — tiny SQLite layer. No ORM, no migrations: just what a hackathon needs.
"""
import sqlite3
from datetime import datetime

DB_PATH = "lostfound.db"
CAMPUS_LOCATIONS = [
    "Library", "Main Gate", "Cafeteria", "Sports Complex",
    "Hostel A", "Hostel B", "Academic Block", "Parking Lot",
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL CHECK(type IN ('lost','found')),
            title       TEXT NOT NULL,
            description TEXT NOT NULL,
            location    TEXT NOT NULL,
            lat         REAL,
            lon         REAL,
            time        TEXT NOT NULL,          -- ISO format
            image_path  TEXT,
            contact     TEXT NOT NULL,          -- email / phone of reporter
            status      TEXT DEFAULT 'open',    -- open | matched | verified
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def insert_report(data):
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO reports (type, title, description, location, lat, lon,
                                time, image_path, contact)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data["type"], data["title"], data["description"], data["location"],
         data.get("lat"), data.get("lon"), data["time"].isoformat(),
         data.get("image_path"), data["contact"]),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def all_reports():
    conn = get_db()
    rows = conn.execute("SELECT * FROM reports ORDER BY time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_report(report_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def set_status(report_id, status):
    conn = get_db()
    conn.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()

def parse_time(iso_str):
    return datetime.fromisoformat(iso_str)

def to_match_input(row):
    """Convert a DB row into the dict shape matching.py expects."""
    return {
        "id": row["id"],
        "type": row["type"],
        "title": row["title"],
        "description": row["description"],
        "location": row["location"],
        "lat": row["lat"],
        "lon": row["lon"],
        "time": parse_time(row["time"]),
        "image_path": row["image_path"],
        "contact": row["contact"],
        "status": row["status"],
    }
