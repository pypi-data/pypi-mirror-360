from pathlib import Path
import os
class Holder:
    LOG_DIR = Path.home() / ".dictionary107"
    LOG_FILE = LOG_DIR / "history.log"

    @staticmethod
    def append_log(action: str, key: str, value: str = ""):
        Holder.LOG_DIR.mkdir(parents=True, exist_ok=True)

        with open(Holder.LOG_FILE, "a", encoding="utf-8") as f:
            if action == "ADD":
                f.write(f"ADD: {key}: {value}\n")
            elif action == "UPDATE":
                f.write(f"UPDATE: {key}: {value}\n")
            elif action == "DELETE":
                f.write(f"DELETE: {key}\n")

    @staticmethod
    def read_log():
        entries = []
        try:
            with open(Holder.LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    entries.append(line.strip())
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error reading log: {e}")
        return entries
