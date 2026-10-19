# The order of the trial. Each step adds exactly one entry to the transcript,
# so the next step is the one at position len(transcript).
# speaker_role is "judge", "prosecution" or "defence".
TRIAL_STAGES = [
    {"stage": "judge_opening", "speaker_role": "judge"},
    {"stage": "opening_statement", "speaker_role": "prosecution"},
    {"stage": "opening_statement", "speaker_role": "defence"},
    {"stage": "present_evidence", "speaker_role": "prosecution"},
    {"stage": "present_evidence", "speaker_role": "defence"},
    {"stage": "judge_instructions", "speaker_role": "judge"},
    # closing_argument and verdict come later
]

# How each stage is called on the page
STAGE_LABELS = {
    "judge_opening": "judge's opening",
    "opening_statement": "opening statement",
    "present_evidence": "presentation of evidence",
    "judge_instructions": "instructions to the jury",
}

# The placeholder of the player's input box for each stage
STAGE_INPUT_HINTS = {
    "opening_statement": "Address the court and the jury. Introduce your theory of the case...",
    "present_evidence": "Walk the jury through your evidence (E1, E2...) and witnesses, and explain what each shows...",
}


# Returns the next step of the trial, or None when the steps defined so far are done
def get_next_stage(trial: dict) -> dict | None:
    completed_steps = len(trial["transcript"])
    if completed_steps < len(TRIAL_STAGES):
        return TRIAL_STAGES[completed_steps]
    return None
