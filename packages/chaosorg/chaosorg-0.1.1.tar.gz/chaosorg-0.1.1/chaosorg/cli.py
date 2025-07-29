import typer
import json
import shutil
from pathlib import Path
from chaosorg.organizer import organize_project, FOLDER_MAP

app = typer.Typer()

@app.command()
def organize():
    """
    Organize files in the current directory.
    """
    current_path = Path.cwd()
    organize_project(current_path)

@app.command("dry-run")
def dry_run_cmd():
    """
    Show what would be moved in the current directory, without actually moving.
    """
    current_path = Path.cwd()
    organize_project(current_path, dry_run=True)

@app.command()
def undo():
    """
    Undo the last organization in the current directory.
    """
    current_path = Path.cwd()
    log_file = current_path / ".chaosorg_log.json"

    if not log_file.exists():
        print("❌ No organization log found. Nothing to undo.")
        raise typer.Exit()

    with open(log_file, "r") as f:
        moves = json.load(f)

    for move in moves:
        src = current_path / move["to"]
        dst = current_path / move["from"]
        dst.parent.mkdir(parents=True, exist_ok=True)

        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Restored: {move['to']} → {move['from']}")
        else:
            print(f"⚠️ Skipped missing file: {src}")

    # Clean up empty folders
    for folder_name in FOLDER_MAP.keys():
        folder = current_path / folder_name
        try:
            folder.rmdir()
        except OSError:
            pass

    log_file.unlink()
    print("Undo completed successfully ✅")

if __name__ == "__main__":
    app()
