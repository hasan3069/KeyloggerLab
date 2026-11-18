
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "test_events.jsonl"
DB_FILE = BASE_DIR / "lab_events.db"


def main():
    if not LOG_FILE.exists():
        print("No test_events.jsonl file found.")
        return

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                text TEXT NOT NULL
            )
        """)

        imported = 0

        with LOG_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                event = json.loads(line)

                connection.execute(
                    """
                    INSERT INTO events (timestamp, event_type, text)
                    VALUES (?, ?, ?)
                    """,
                    (
                        event["timestamp"],
                        event["event_type"],
                        event["text"],
                    ),
                )
                imported += 1

        connection.commit()

        total = connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

    print(f"Imported {imported} event(s).")
    print(f"Total events in database: {total}")
    print(f"Database created at: {DB_FILE}")


if __name__ == "__main__":
    main()
