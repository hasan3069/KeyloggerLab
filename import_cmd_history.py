
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "cmd_history.jsonl"
DB_FILE = BASE_DIR / "lab_events.db"

with sqlite3.connect(DB_FILE) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cmd_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            command TEXT NOT NULL,
            UNIQUE(timestamp, command)
        )
    """)

    imported = 0

    with JSON_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            event = json.loads(line)

            cursor = conn.execute("""
                INSERT OR IGNORE INTO cmd_history
                (timestamp, event_type, command)
                VALUES (?, ?, ?)
            """, (
                event["timestamp"],
                event["event_type"],
                event["command"]
            ))

            imported += cursor.rowcount

print(f"Imported {imported} new command record(s).")
print(f"Database: {DB_FILE}")
