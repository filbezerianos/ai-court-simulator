import json
import os
import tempfile
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"

DEFAULTS = {
    "user_name": "Alex Morgan",
    "judge_name": "Judge Eleanor Whitmore-Hayes",
    "opponent_name": "Jordan Ellis",
    "model": "gemma4:e2b",
}

# Read the settings.json and load settings
def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return {**DEFAULTS, **json.load(f)}
    except FileNotFoundError:

        # If the file is missing return the default values above
        return dict(DEFAULTS)

# Save settings back to settings.json. Use a tmp file in case of an app crash
def save_settings(settings: dict) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=SETTINGS_FILE.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, SETTINGS_FILE)