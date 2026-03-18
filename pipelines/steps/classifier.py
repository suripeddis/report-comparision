import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def classify_transcript(transcript_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert analyst of AAC (Augmentative and Alternative Communication) "
                    "letterboarding therapy sessions. Given a transcript of a session, identify every "
                    "utterance made by the facilitator that functions as a prompt directed at the student, "
                    "then classify each into exactly one of the following categories:\n\n"
                    "Choice Prompt — offers the student discrete, explicit options to select from.\n"
                    "Example: 'Do you want to do this one, or this one?'\n\n"
                    "Clarification Prompt — asks the student to confirm, correct, or expand on something "
                    "they already communicated.\n"
                    "Example: 'Did you mean brings, or something else?'\n\n"
                    "Guided Prompt — scaffolds the student toward a specific target answer, often by "
                    "providing letter cues, partial words, or directional hints.\n"
                    "Example: 'It starts with S — find it.' / 'Move your eyes up to the top row.'\n\n"
                    "Open-ended Prompt — invites the student to generate a response freely with no "
                    "constraints or target answer implied.\n"
                    "Example: 'What are you noticing in this picture?'\n\n"
                    "Reinforcement Prompt — encourages the student to continue, affirm their effort, "
                    "or regulate emotionally. Does not elicit new information but sustains engagement.\n"
                    "Example: 'You're doing great, keep going.' / 'Tell yourself you're doing well.'\n\n"
                    "When a prompt could fit multiple categories, use these rules:\n"
                    "- If the facilitator provides letter cues OR partial spelling → Guided, even if phrased as a question\n"
                    "- 'What do you see?' with no prior student output → Open-ended\n"
                    "- 'What do you see?' immediately after the student partially spelled something → Clarification\n"
                    "- If options are listed explicitly → Choice, even if the sentence starts with 'what' or 'do you want'\n"
                    "- Encouragement mid-task that also nudges continuation → Reinforcement, not Guided\n\n"
                    "Return ONLY a JSON array. Each object must contain:\n"
                    "- timestamp — from the transcript\n"
                    "- prompt_text — the facilitator's exact words\n"
                    "- type — one of: choice, clarification, guided, open_ended, reinforcement\n\n"
                    "No explanation, no preamble, no markdown. Only the JSON array."
                )
            },
            {
                "role": "user",
                "content": transcript_text
            }
        ]
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)
