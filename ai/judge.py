from ai.llm import ask, load_prompt, format_transcript_for_prompt
from store.case_store import load_case, add_entry

# The verdict rule the judge explains to the jury
VERDICT_RULE = "unanimous, agreed by all twelve jurors"

# The prompt of each judge stage is prompts/<stage>.md
JUDGE_WORD_COUNTS = {"judge_opening": 200, "judge_instructions": 300}


# The judge speaks at the given stage. The speech is saved in the transcript and returned.
async def generate_judge_statement(stage: str) -> str:
    trial = load_case()
    case = trial["case"]
    judge = trial["cast"]["judge"]

    prompt = load_prompt(
        stage,
        judge_name=judge["name"],
        judge_personality=judge["personality"],
        case_title=case["title"],
        charge=case["charge"],
        defendant=case["defendant"],
        transcript=format_transcript_for_prompt(trial),
        verdict_rule=VERDICT_RULE,
        word_count=JUDGE_WORD_COUNTS[stage],
    )
    text = await ask(prompt)
    add_entry(judge["name"], "judge", stage, text)
    return text


# The judge opens the trial
async def judge_opening() -> str:
    return await generate_judge_statement("judge_opening")


# The judge instructs the jury before the verdict
async def judge_jury_instructions() -> str:
    return await generate_judge_statement("judge_instructions")
