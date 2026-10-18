import json
import os
import tempfile
from pathlib import Path

# The json file with the jurors
JURY_FILE = Path(__file__).parent / "data" / "jury.json"

# The default jurors, used to reset the jury
DEFAULT_JURY_FILE = Path(__file__).parent / "data" / "jury_default.json"


def load_jury() -> list[dict]:
    with open(JURY_FILE, encoding="utf-8") as f:
        return json.load(f)["jurors"]


# Write to a temp file first in case of an app crash
def save_jury(jurors: list[dict]) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=JURY_FILE.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"jurors": jurors}, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, JURY_FILE)


# Overwrite the jurors with the defaults and return them
def reset_jury() -> list[dict]:
    with open(DEFAULT_JURY_FILE, encoding="utf-8") as f:
        jurors = json.load(f)["jurors"]
    save_jury(jurors)
    return jurors