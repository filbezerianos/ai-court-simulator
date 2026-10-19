from ai.llm import ask, load_prompt, format_transcript_for_prompt
from store.case_store import load_case, add_entry

SIDE_TITLES = {"prosecution": "prosecuting attorney", "defence": "defence attorney"}

# The task prompt (prompts/<name>.md) used for each trial stage
STATEMENT_PROMPTS = {"opening_statement": "opening", "present_evidence": "present_evidence"}

STATEMENT_WORD_COUNTS = {"opening_statement": 250, "present_evidence": 350}


def format_evidence_for_prompt(case: dict) -> str:
    return "\n".join(f"E{number}: {item}" for number, item in enumerate(case["evidence"], start=1))


def format_witnesses_for_prompt(case: dict) -> str:
    return "\n".join(f"- {witness}" for witness in case["witnesses"])


# The AI opponent speaks for its side at the given stage. The speech is saved in the transcript and returned.
async def generate_opponent_statement(stage: str) -> str:
    trial = load_case()
    case = trial["case"]
    judge = trial["cast"]["judge"]
    player = trial["cast"]["player"]
    opponent = trial["cast"]["opponent"]
    side = opponent["side"]

    system_prompt = load_prompt(
        "lawyer_system",
        opponent_name=opponent["name"],
        opponent_personality=opponent["personality"],
        side=side,
        side_title=SIDE_TITLES[side],
        user_name=player["name"],
        judge_name=judge["name"],
        case_title=case["title"],
        charge=case["charge"],
        defendant=case["defendant"],
        summary=case["summary"],
        context=case["context"],
        evidence=format_evidence_for_prompt(case),
        witnesses=format_witnesses_for_prompt(case),
    )
    task_prompt = load_prompt(
        STATEMENT_PROMPTS[stage],
        side=side,
        transcript=format_transcript_for_prompt(trial),
        word_count=STATEMENT_WORD_COUNTS[stage],
    )

    text = await ask(task_prompt, system=system_prompt)
    add_entry(opponent["name"], side, stage, text)
    return text
