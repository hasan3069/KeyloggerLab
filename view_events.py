
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "lab_events.db"

with sqlite3.connect(DB_FILE) as connection:
    cursor = connection.execute("""
        SELECT id, timestamp, event_type, text
        FROM events
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

if not rows:
    print("No events found.")
else:
    for event_id, timestamp, event_type, text in rows:
        print("-" * 50)
        print(f"ID: {event_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Event type: {event_type}")
        print(f"Text: {text}")
