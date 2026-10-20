import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

# The json file with the current case, the cast and the transcript
CURRENT_CASE_FILE = Path(__file__).parent.parent / "data" / "current_case.json"

# The folder with the finished cases the player decided to keep
SAVED_CASES_FOLDER = Path(__file__).parent.parent / "data" / "saved_cases"


# Returns None when there is no case yet (missing, empty or "{}" file)
def load_case() -> dict | None:
    try:
        with open(CURRENT_CASE_FILE, encoding="utf-8") as f:
            trial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return trial or None


# Write to a temp file first in case of an app crash
def save_case(trial: dict) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=CURRENT_CASE_FILE.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(trial, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, CURRENT_CASE_FILE)


# Record the side the player takes. The opponent gets the other side.
def choose_side(side: str) -> None:
    trial = load_case()
    trial['cast']['player']['side'] = side
    trial['cast']['opponent']['side'] = 'defence' if side == 'prosecution' else 'prosecution'
    save_case(trial)


# Append one entry (a speech) to the transcript of the current trial
def add_entry(speaker: str, role: str, stage: str, text: str) -> None:
    trial = load_case()
    trial['transcript'].append({'speaker': speaker, 'role': role, 'stage': stage, 'text': text})
    save_case(trial)


# Save the result of one round of jury decisions. A tie leads to another round later.
def add_verdict_round(round_result: dict) -> None:
    trial = load_case()
    trial.setdefault('verdict', {'rounds': []})['rounds'].append(round_result)
    save_case(trial)


# Keep a copy of the current case in data/saved_cases. The date and time (YYYYMMDDHHmmss)
# is appended to the file name, so the saved cases do not overwrite each other.
def save_case_copy() -> Path:
    SAVED_CASES_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_file = SAVED_CASES_FOLDER / f"{CURRENT_CASE_FILE.stem}_{timestamp}.json"
    shutil.copy2(CURRENT_CASE_FILE, saved_file)
    return saved_file


# Remove the current case, so the Courtroom tab goes back to the Generate Case button
def clear_case() -> None:
    save_case({})
