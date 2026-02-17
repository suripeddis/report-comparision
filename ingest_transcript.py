import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPEN_API_KEY"))

def read_transcript(file_uploaded):
    document = file_uploaded.read()
    document = document.decode("utf-8", errors="replace")

    pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n"
    cleaned_content = re.sub(pattern, "", document)

    lines = cleaned_content.splitlines()
    print("TOTAL LINES AFTER CLEAN:", len(lines))
    return lines

def is_prompt(line: str) -> bool:
    l = line.strip().lower()

    if not l:
        return False

    # Questions
    if "?" in l:
        return True

    # Choice structure
    if " or " in l:
        return True

    prompt_starters = (
        "tell me",
        "show me",
        "spell",
        "choose",
        "pick",
        "point",
        "say",
        "look",
        "find",
        "read",
        "write",
        "give me",
        "let’s",
        "lets",
    )
    for starter in prompt_starters:
        if l.startswith(starter):
            return True

    recall_phrases = (
        "do you remember",
        "what happened",
        "what comes next",
        "why do you think",
        "how did",
        "can you",
    )
    for phrase in recall_phrases:
        if phrase in l:
            return True

    return False

def open_ai_send(line: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the given line in TWO ways and return exactly TWO labels on ONE line.\n\n"
                    "Format (return exactly this):\n"
                    "METHOD | PROMPT_TYPE\n\n"
                    "METHOD labels (KPI):\n"
                    "S2C | RPM | Mixed | Unclear\n\n"
                    "PROMPT_TYPE labels (Graph):\n"
                    "Guided | Open-ended | Clarification | Reinforcement | Choice-based | Other/Unclear\n\n"
                    "METHOD definitions:\n"
                    "S2C:\n"
                    "- Invites independent generation\n"
                    "- Open-ended\n"
                    "- No embedded choices/options\n"
                    "- No directive cueing\n\n"
                    "RPM:\n"
                    "- Scaffolded/structured prompting\n"
                    "- Embedded choices/options or directive cueing\n"
                    "- Narrows/structures the response\n\n"
                    "Mixed:\n"
                    "- Contains BOTH open-ended + scaffold/choices/directives\n\n"
                    "Unclear:\n"
                    "- Not enough evidence to classify method\n\n"
                    "PROMPT_TYPE definitions:\n"
                    "Guided:\n"
                    "- Step-by-step or directive prompting\n"
                    "- Tells the speller what to do or how to respond\n"
                    "- Examples: 'Spell MADE', 'Start with the first sound'\n\n"
                    "Open-ended:\n"
                    "- Allows spontaneous, reflective responses\n"
                    "- No embedded choices\n"
                    "- Examples: 'What do you think?', 'Why do you suppose?'\n\n"
                    "Clarification:\n"
                    "- Requests explanation/expansion of a prior response\n"
                    "- Example: 'Can you explain what you meant by SOFT?'\n\n"
                    "Reinforcement:\n"
                    "- Praise or encouragement\n"
                    "- Examples: 'Nice job hanging in there', 'That’s a great thought'\n\n"
                    "Choice-based:\n"
                    "- Offers 2–3 options\n"
                    "- Example: 'Do you want the doll or the poem?'\n\n"
                    "Rules:\n"
                    "- If the line is not a true prompt, return: Unclear | Other/Unclear\n"
                    "- Return ONLY the two labels in the exact format: METHOD | PROMPT_TYPE\n"
                    "- No extra words"
                ),
            },
            {"role": "user", "content": line},
        ],
    )

    return response.choices[0].message.content.strip()
