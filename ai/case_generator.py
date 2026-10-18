import json
import random
from pathlib import Path
from string import Template

from ollama import AsyncClient
from pydantic import BaseModel

from case_store import save_case
from settings_store import load_settings

ROOT = Path(__file__).parent.parent
PROMPT_FILE = ROOT / "prompts" / "case_generate.md"
TOPICS_FILE = ROOT / "data" / "case_topics.json"

MAX_ATTEMPTS = 3


# The fields (and their order) must match prompts/case_generate.md
class Case(BaseModel):
    title: str
    charge: str
    defendant: str
    summary: str
    context: str
    twist: str
    evidence: list[str]
    witnesses: list[str]
    judge_personality: str
    opponent_personality: str


# Fill the placeholders of the prompt with a random topic/setting and the names from the settings
def build_prompt(settings: dict) -> str:
    topics = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    template = Template(PROMPT_FILE.read_text(encoding="utf-8"))
    return template.substitute(
        topic=random.choice(topics["topics"]),
        setting=random.choice(topics["settings"]),
        user_name=settings["user_name"],
        opponent_name=settings["opponent_name"],
        judge_name=settings["judge_name"],
    )


# Group the generated case and the names from the settings into the sections of the saved file
def build_trial(case: Case, settings: dict) -> dict:
    return {
        "case": case.model_dump(exclude={"judge_personality", "opponent_personality"}),
        "cast": {
            "judge": {"name": settings["judge_name"], "personality": case.judge_personality},
            "opponent": {"name": settings["opponent_name"], "personality": case.opponent_personality, "side": None},
            "player": {"name": settings["user_name"], "side": None},
        },
        "transcript": [],
    }


async def generate_case() -> Case:
    settings = load_settings()
    prompt = build_prompt(settings)

    last_error = None
    for _ in range(MAX_ATTEMPTS):
        response = await AsyncClient().chat(
            model=settings["model"],
            messages=[{"role": "user", "content": prompt}],
            format=Case.model_json_schema(),
            options={"temperature": 0.9},
        )
        try:
            case = Case.model_validate_json(response.message.content)
        except ValueError as e:  # pydantic's ValidationError is a ValueError
            last_error = e
            continue
        save_case(build_trial(case, settings))
        return case

    raise RuntimeError(f"Could not generate a valid case: {last_error}")


# Quick test without the UI: python -m ai.case_generator
if __name__ == "__main__":
    import asyncio

    print(asyncio.run(generate_case()).model_dump_json(indent=2))
