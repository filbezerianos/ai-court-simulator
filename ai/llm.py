from pathlib import Path
from string import Template
from ollama import AsyncClient
from store.settings_store import load_settings

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# Read prompts/<name>.md and fill in its $placeholders
def load_prompt(name: str, **values) -> str:
    template = Template((PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8"))
    return template.substitute(**values)


# Ask the model from the settings and return its text answer
async def ask(prompt: str, system: str | None = None, temperature: float = 0.7) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await AsyncClient().chat(
        model=load_settings()["model"],
        messages=messages,
        options={"temperature": temperature},
    )
    return response.message.content.strip()


# The transcript as plain text, to fill the $transcript placeholder of the prompts
def format_transcript_for_prompt(trial: dict) -> str:
    if not trial["transcript"]:
        return "(nothing has been said yet)"
    return "\n\n".join(
        f"{entry['speaker']} ({entry['role']}, {entry['stage'].replace('_', ' ')}):\n{entry['text']}"
        for entry in trial["transcript"]
    )
