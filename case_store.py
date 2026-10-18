import json
import os
import tempfile
from pathlib import Path

# The json file with the current case, the cast and the transcript
CASE_FILE = Path(__file__).parent / "data" / "current_case.json"


# Returns None when there is no case yet (missing, empty or "{}" file)
def load_case() -> dict | None:
    try:
        with open(CASE_FILE, encoding="utf-8") as f:
            trial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return trial or None


# Write to a temp file first in case of an app crash
def save_case(trial: dict) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=CASE_FILE.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(trial, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, CASE_FILE)


# Remove the current case, so the Courtroom tab goes back to the Generate Case button
def clear_case() -> None:
    save_case({})
