
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "windows_events.jsonl"
DB_FILE = BASE_DIR / "lab_events.db"


def main():
    if not INPUT_FILE.exists():
        print("Windows event file not found.")
        return

    imported = 0

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS windows_process_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_id INTEGER NOT NULL,
                process_name TEXT NOT NULL,
                process_path TEXT,
                parent_path TEXT,
                username TEXT,
                UNIQUE(timestamp, event_id, process_path, parent_path)
            )
        """)

        with INPUT_FILE.open("r", encoding="utf-8-sig") as file:
            records = json.load(file)

        # PowerShell outputs an object for one result
        # and an array for multiple results.
        if isinstance(records, dict):
            records = [records]

        for event in records:
            cursor = connection.execute("""
                INSERT OR IGNORE INTO windows_process_events
                (timestamp, event_id, process_name, process_path,
                 parent_path, username)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event["timestamp"],
                event["event_id"],
                event["process_name"],
                event.get("process_path"),
                event.get("parent_path"),
                event.get("username"),
            ))

            imported += cursor.rowcount

        total = connection.execute("""
            SELECT COUNT(*) FROM windows_process_events
        """).fetchone()[0]

    print(f"New events imported: {imported}")
    print(f"Total Windows events in database: {total}")


if __name__ == "__main__":
    main()
 