import os
import shutil
from pathlib import Path
import json

# Mapping of extensions to folder names
FOLDER_MAP = {
    "data": [".csv", ".xls", ".xlsx"],
    "notebooks": [".ipynb"],
    "scripts": [".py"],
    "outputs": [".png", ".jpg", ".jpeg"],
    "models": [".pkl", ".joblib", ".h5"],
    "docs": [".md", ".txt", ".docx", ".pdf"]
}

def organize_project(folder_path=".", dry_run=False):
    """
    Organizes files in the given folder by moving them into subfolders
    based on their extensions.

    Parameters:
        folder_path (str): Path to the folder you want to organize.
        dry_run (bool): If True, simulate organization without actually moving files.
    """
    base = Path(folder_path)
    log = []

    for folder_name, extensions in FOLDER_MAP.items():
        files_to_move = [
            f for f in base.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        ]

        if files_to_move:
            target_folder = base / folder_name
            if not dry_run:
                target_folder.mkdir(exist_ok=True)

            for file in files_to_move:
                destination = target_folder / file.name

                if file.parent == target_folder:
                    continue  # Already sorted

                if dry_run:
                    print(f"[DRY RUN] Would move: {file.name} → {folder_name}/")
                else:
                    shutil.move(str(file), str(destination))
                    print(f"Moved: {file.name} → {folder_name}/")
                    log.append({"from": str(file), "to": str(destination)})

    if not dry_run:
        # Save undo log
        log_path = Path(folder_path) / ".chaosorg_log.json"
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
        print(f"Log saved to {log_path}")

    print("Organization Done ✅ (dry run)" if dry_run else "Organization Done ✅")
