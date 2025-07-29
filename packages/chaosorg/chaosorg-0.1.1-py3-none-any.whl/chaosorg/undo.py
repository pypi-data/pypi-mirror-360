import json
import shutil
from pathlib import Path

def undo_organization(folder_path="."):
    base = Path(folder_path)
    log_file = base / ".chaosorg_log.json"

    # Check if log exists
    if not log_file.exists():
        print("❌ No chaosorg log found. Nothing to undo.")
        return

    with open(log_file, "r") as f:
        moves = json.load(f)

    # Reverse the moves
    for entry in moves:
        src = Path(entry["to"])
        dst = Path(entry["from"])

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"Moved back: {src.name} → {dst.parent}")
        else:
            print(f"⚠️ Skipped (not found): {src}")

    # Delete the log
    log_file.unlink()
    print("Undo completed ✅")

if __name__ == "__main__":
    current_dir = Path.cwd()
    print(f"Undoing chaosorg organization in: {current_dir}")
    undo_organization(current_dir)
