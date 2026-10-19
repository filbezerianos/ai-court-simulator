import json
import os
import tempfile
from pathlib import Path

# The json file with the current case, the cast and the transcript
CURRENT_CASE_FILE = Path(__file__).parent.parent / "data" / "current_case.json"


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


# Remove the current case, so the Courtroom tab goes back to the Generate Case button
def clear_case() -> None:
    save_case({})
