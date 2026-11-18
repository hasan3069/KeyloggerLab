from datetime import datetime
from pathlib import Path
import sqlite3
from flask import Flask, jsonify, render_template_string, request

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "lab_events.db"

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CMD Command History</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 35px auto;
            padding: 0 18px;
            background: #f4f6fa;
            color: #172033;
        }
        .muted { color: #596579; }
        .panel {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 2px 8px #0000000c;
        }
        input {
            padding: 10px;
            width: min(350px, 90%);
            border: 1px solid #ccd3df;
            border-radius: 6px;
        }
        button {
            padding: 10px 14px;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
            background: #2457d6;
            color: white;
        }
        .table-wrap { overflow-x: auto; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 14px;
        }
        th, td {
            text-align: left;
            padding: 11px;
            border-bottom: 1px solid #e5e9f0;
            font-size: 14px;
        }
        th { background: #eef2f8; }
        code { overflow-wrap: anywhere; }
    </style>
</head>
<body>
    <h1>CMD Command History</h1>
    <p class="muted">
        Local dashboard showing commands entered in your dedicated lab terminal.
    </p>

    <section class="panel">
        <h2>Recorded Commands</h2>
        <p id="count" class="muted">Loading commands...</p>
        <input id="search" type="search"
               placeholder="Search commands">
        <button id="refresh">Refresh</button>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Command</th>
                        <th>Event Type</th>
                    </tr>
                </thead>
                <tbody id="commands"></tbody>
            </table>
        </div>
    </section>

    <script>
        const tbody = document.getElementById("commands");
        const search = document.getElementById("search");
        const count = document.getElementById("count");
        let allCommands = [];

        function cell(value) {
            const td = document.createElement("td");
            td.textContent = value ?? "";
            return td;
        }

        function render() {
            const term = search.value.toLowerCase();

            const filtered = allCommands.filter(item =>
                (item.command || "").toLowerCase().includes(term) ||
                (item.event_type || "").toLowerCase().includes(term)
            );

            tbody.replaceChildren();

            for (const item of filtered) {
                const row = document.createElement("tr");
                row.append(
                    cell(item.timestamp),
                    cell(item.command),
                    cell(item.event_type)
                );
                tbody.appendChild(row);
            }

            count.textContent =
                `${filtered.length} matching command(s) · ` +
                `${allCommands.length} loaded`;
        }

        async function loadCommands() {
            count.textContent = "Loading commands...";
            try {
                const response = await fetch("/api/commands");
                if (!response.ok) throw new Error("Request failed");
                allCommands = await response.json();
                render();
            } catch (error) {
                count.textContent =
                    "Could not load commands. Check the server terminal.";
            }
        }

        search.addEventListener("input", render);
        document.getElementById("refresh")
            .addEventListener("click", loadCommands);

        loadCommands();
    </script>
</body>
</html>
"""


@app.get("/")
def dashboard():
    return render_template_string(PAGE)


@app.get("/api/commands")
def get_commands():
    search = request.args.get("search", "").strip()[:100]

    query = """
        SELECT timestamp, command, event_type
        FROM cmd_history
    """
    params = []

    if search:
        query += " WHERE command LIKE ? OR event_type LIKE ?"
        pattern = f"%{search}%"
        params.extend([pattern, pattern])

    query += " ORDER BY id DESC LIMIT 500"

    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, params).fetchall()

    return jsonify([dict(row) for row in rows])

from datetime import datetime, timezone

@app.post("/api/keystroke-events")
def save_keystroke_event():
    data = request.get_json(silent=True) or {}

    event_type = data.get("event_type", "")
    key_category = data.get("key_category", "")
    sequence = data.get("sequence")

    if event_type not in ("keydown", "keyup"):
        return jsonify({"error": "Invalid event type"}), 400

    if key_category not in ("character-key", "control-key"):
        return jsonify({"error": "Invalid key category"}), 400

    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        return jsonify({"error": "Invalid sequence"}), 400

    timestamp = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS keystroke_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                key_category TEXT NOT NULL
            )
        """)

        connection.execute("""
            INSERT INTO keystroke_events
                (timestamp, sequence, event_type, key_category)
            VALUES (?, ?, ?, ?)
        """, (timestamp, sequence, event_type, key_category))

    return jsonify({"status": "saved"}), 201

@app.get("/keystroke-lab")
def keystroke_lab():
    return (BASE_DIR / "keystroke_lab.html").read_text(encoding="utf-8")


@app.post("/api/lab-text")
def save_lab_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text")

    if not isinstance(text, str):
        return jsonify({"error": "Text is required"}), 400

    if len(text) > 10000:
        return jsonify({"error": "Text is too long"}), 413

    timestamp = datetime.now().astimezone().isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
           "INSERT INTO events (timestamp, event_type, text) VALUES (?, ?, ?)",
            (timestamp, "test_input", text)
        )

    return jsonify({"status": "saved", "timestamp": timestamp}), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
