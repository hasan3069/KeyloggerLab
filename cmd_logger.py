
import json
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).with_name("cmd_history.jsonl")

print("Local CMD Command Logger")
print("Type a command and press Enter to execute it.")
print("Type 'exit' to stop the logger.")
print("-" * 45)

while True:
    try:
        command = input("Lab-CMD> ").strip()

        if not command:
            continue

        if command.lower() == "exit":
            break

        event = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "event_type": "cmd_command",
            "command": command,
        }

        with LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")

        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            errors="replace",
        )

        if result.stdout:
            print(result.stdout, end="")

        if result.stderr:
            print(result.stderr, end="")

        print(f"[Exit code: {result.returncode}]")

    except (KeyboardInterrupt, EOFError):
        print("\nLogger stopped.")
        break
