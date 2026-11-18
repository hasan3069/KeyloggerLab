
import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

LOG_FILE = Path(__file__).with_name("test_events.jsonl")


def save_test_text():
    text = input_box.get("1.0", "end-1c").strip()

    if not text:
        messagebox.showwarning("Empty input", "Please enter some test text.")
        return

    event = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "event_type": "test_input",
        "text": text,
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    input_box.delete("1.0", tk.END)
    messagebox.showinfo("Saved", f"Test text saved to:\n{LOG_FILE.name}")


root = tk.Tk()
root.title("Cybersecurity Lab - Input Simulator")
root.geometry("520x350")

heading = tk.Label(
    root,
    text="Local Input Simulator",
    font=("Arial", 16, "bold"),
)
heading.pack(pady=12)

instructions = tk.Label(
    root,
    text="Enter sample text below. Only text submitted in this window is recorded.",
    wraplength=460,
)
instructions.pack(pady=5)

input_box = tk.Text(root, height=7, width=55)
input_box.pack(padx=15, pady=10)

save_button = tk.Button(
    root,
    text="Save Test Event",
    command=save_test_text,
)
save_button.pack(pady=8)

root.mainloop()
