import asyncio
from typing import Literal

from pydantic import BaseModel

from ai.llm import ask, load_prompt, format_transcript_for_prompt
from store.case_store import load_case, add_verdict_round
from store.jury_store import load_jury

MAX_ATTEMPTS = 3


# The fields (and their order) of the juror's answer. The rationale comes first,
# so the juror explains before deciding.
class JurorVote(BaseModel):
    rationale: str
    decision: Literal["guilty", "not guilty"]


# The text of the judge's instructions, taken from the transcript
def get_judge_instructions(trial: dict) -> str:
    for entry in trial["transcript"]:
        if entry["stage"] == "judge_instructions":
            return entry["text"]
    return "(the judge gave no instructions)"


# One juror decides, based on the trial and on who the juror is (age, occupation, bias).
# Returns {"juror_id", "name", "decision", "rationale"}.
async def get_juror_vote(juror: dict, trial: dict) -> dict:
    case = trial["case"]

    bias_line = f"Your personal outlook: {juror['bias']}" if juror.get("bias") else ""
    system_prompt = load_prompt(
        "juror_system",
        juror_name=juror["name"],
        juror_age=juror["age"],
        juror_occupation=juror["occupation"],
        bias_line=bias_line,
    )
    task_prompt = load_prompt(
        "juror_verdict",
        case_title=case["title"],
        charge=case["charge"],
        defendant=case["defendant"],
        transcript=format_transcript_for_prompt(trial),
        judge_instructions=get_judge_instructions(trial),
    )

    for _ in range(MAX_ATTEMPTS):
        answer = await ask(
            task_prompt,
            system=system_prompt,
            temperature=0.8,
            response_schema=JurorVote.model_json_schema(),
        )
        try:
            vote = JurorVote.model_validate_json(answer)
        except ValueError:  # pydantic's ValidationError is a ValueError
            continue
        return {
            "juror_id": juror["id"],
            "name": juror["name"],
            "decision": vote.decision,
            "rationale": vote.rationale.strip(),
        }

    raise RuntimeError(f"{juror['name']} could not reach a decision")


# Count the votes. The result is "guilty", "not guilty" or "tie" (6 against 6).
def tally_votes(votes: list[dict]) -> dict:
    guilty = sum(1 for vote in votes if vote["decision"] == "guilty")
    not_guilty = len(votes) - guilty
    if guilty > not_guilty:
        result = "guilty"
    elif not_guilty > guilty:
        result = "not guilty"
    else:
        result = "tie"
    return {"votes": votes, "guilty": guilty, "not_guilty": not_guilty, "result": result}


# The player wins when the prosecution gets "guilty" or the defence gets "not guilty"
def did_player_win(player_side: str, result: str) -> bool:
    return (player_side == "prosecution" and result == "guilty") or (
        player_side == "defence" and result == "not guilty"
    )


# All the jurors decide at the same time. on_juror_decided(vote) is called as each one finishes,
# so the page can replace the dots with the decision. The round is saved and returned.
async def run_jury_deliberation(on_juror_decided=None) -> dict:
    trial = load_case()
    jurors = load_jury()

    async def decide(juror: dict) -> dict:
        vote = await get_juror_vote(juror, trial)
        if on_juror_decided:
            on_juror_decided(vote)
        return vote

    tasks = [asyncio.create_task(decide(juror)) for juror in jurors]
    try:
        votes = await asyncio.gather(*tasks)
    except Exception:
        # One juror failed, stop the others and let the caller handle the error
        for task in tasks:
            task.cancel()
        raise

    round_result = tally_votes(list(votes))
    add_verdict_round(round_result)
    return round_result
