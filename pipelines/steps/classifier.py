import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_secret(name: str):
    """Read a config value from the environment, falling back to Streamlit secrets."""
    val = os.getenv(name)
    if val:
        return val
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return None


def _get_client():
    global _client
    if _client is None:
        api_key = _get_secret("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set. Locally, check your .env file; "
                "on Streamlit Cloud, set it in the app's Secrets."
            )
        _client = OpenAI(api_key=api_key)
    return _client

def _extract_json(raw: str) -> list:
    """Parse the model response robustly regardless of formatting."""
    # Strip markdown code fences: ```json ... ``` or ``` ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # If the model added prose before/after the array, pull out the array
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    return json.loads(raw)


def classify_transcript(transcript_text):
    response = _get_client().chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        seed=42,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert analyst of AAC (Augmentative and Alternative Communication) "
                    "letterboarding therapy sessions. Given a transcript of a session, identify every "
                    "utterance made by the facilitator that is directed at or intended for the student — "
                    "including questions, instructions, motor guidance, regulation support, encouragement, "
                    "and topic-related comments. Only exclude talk clearly directed at a parent, observer, "
                    "or another adult in the room (not the student). "
                    "Classify each facilitator utterance along three dimensions. "
                    "FIRST decide the METHOD (Dimension 1), then choose a TYPE from the vocabulary "
                    "that belongs to that method (Dimension 2).\n\n"

                    "── DIMENSION 1: METHOD ──\n"
                    "Classify each prompt as belonging to one of two AAC methodologies:\n\n"
                    "S2C (Spelling to Communicate) — prompts rooted in motor learning and regulation. "
                    "Characteristic markers: direct letterboard navigation cues (row/column direction, "
                    "arm/hand placement), body regulation support (breathing, stillness, re-focusing), "
                    "physical or gestural scaffolding, and prompts that guide the motor act of pointing "
                    "rather than the content of a response.\n"
                    "Examples: 'Move your arm up.' / 'Take a breath and reset.' / 'Find the top row.' / "
                    "'Open your hand.' / 'Eyes on the board.'\n\n"
                    "RPM (Rapid Prompting Method) — prompts rooted in academic engagement and content. "
                    "Characteristic markers: academic or factual questions, topic-driven open-ended prompts, "
                    "sensory/auditory engagement cues, subject-matter choices, and prompts that emphasize "
                    "the cognitive content of the response rather than the motor process.\n"
                    "Examples: 'What is the main idea of the paragraph?' / 'Choose: volcano or earthquake?' / "
                    "'Listen to this sentence — what word is missing?' / 'Tell me about the character.'\n\n"
                    "Decision rule: if a prompt addresses BOTH motor process and content, classify by its "
                    "primary intent — motor guidance → S2C, content engagement → RPM.\n\n"

                    "── DIMENSION 2: PROMPT TYPE (method-dependent vocabulary) ──\n"
                    "Use the vocabulary that matches the method you chose in Dimension 1.\n\n"

                    "If method = s2c, pick exactly one of these five S2C types:\n"
                    "  initiation — Verbal cue to start movement. Examples: 'Let\'s begin.' / 'Go ahead.' / "
                    "'Spell it now.'\n"
                    "  continuation — Verbal cue to continue movement already in progress. Examples: "
                    "'Keep going.' / 'What comes next?' / 'You\'ve got this.'\n"
                    "  gesture — Physical cue such as pointing or guiding (gesture or hand-based prompt). "
                    "Examples: facilitator points to the board / taps near a row / demonstrates the motion.\n"
                    "  direction — Verbal spatial cue like 'top row' or 'right side'. Examples: "
                    "'Top row.' / 'Move your arm right.' / 'Eyes on the board.'\n"
                    "  none — Independent selection without prompting; facilitator utterances that aren\'t "
                    "really a prompt at all (acknowledgement, narration, off-task chatter). Use this when "
                    "no other S2C type fits.\n\n"

                    "If method = rpm, pick exactly one of these five RPM types:\n"
                    "  choice — Offers the student discrete, explicit options to select from. Example: "
                    "'Do you want to do this one, or this one?'\n"
                    "  clarification — Asks the student to confirm, correct, or expand on something they "
                    "already communicated. Example: 'Did you mean brings, or something else?'\n"
                    "  guided — Scaffolds the student toward a specific target answer via letter cues, "
                    "partial words, or directional hints. Example: 'It starts with S — find it.'\n"
                    "  open_ended — Invites the student to generate a response freely with no constraints "
                    "or target answer implied. Example: 'What are you noticing in this picture?'\n"
                    "  reinforcement — Encourages the student to continue, affirms effort, or regulates "
                    "emotionally without eliciting new information. Example: 'You\'re doing great, keep going.'\n\n"

                    "Tie-breaking rules (apply only within the chosen method vocab):\n"
                    "- RPM, letter cues OR partial spelling → guided, even if phrased as a question\n"
                    "- RPM, 'What do you see?' with no prior student output → open_ended\n"
                    "- RPM, 'What do you see?' right after the student partially spelled something → clarification\n"
                    "- RPM, options listed explicitly → choice\n"
                    "- S2C, spatial words (top/bottom/left/right/row/column) → direction\n"
                    "- S2C, physical pointing / tapping / demonstrating motion → gesture\n"
                    "- S2C, 'keep going' style mid-task cue → continuation\n"
                    "- S2C, opener to begin spelling → initiation\n"
                    "- S2C, no clear S2C prompt action → none\n\n"

                    "── DIMENSION 3: DIWAKAR'S LAB PROMPT TYPES (multi-label) ──\n"
                    "A single prompt can carry MULTIPLE Diwakar's Lab labels — return all that apply, "
                    "from the following set:\n\n"
                    "encouragement — Motivational or supportive language used to keep the participant "
                    "engaged and willing to continue. Example: 'You can do this, keep trying.'\n\n"
                    "dictation — Directly telling or spelling the target response for the participant. "
                    "Example: 'It's S-T-A-R.' / 'The answer is volcano.'\n\n"
                    "instruction — Explicit guidance explaining what action the participant should take. "
                    "Example: 'Pick up the stylus.' / 'Tap the letter.'\n\n"
                    "stm — Short term memory support prompts that help the participant recall or retain "
                    "information temporarily. Example: 'Remember, we just read about the earthquake.'\n\n"
                    "question — Asking the participant something to prompt thinking, recall, or response. "
                    "Example: 'What did the character feel?'\n\n"
                    "hands — Physical hand guidance or demonstrations showing how to interact with the "
                    "system. Example: 'Like this — open your hand and point.'\n\n"
                    "directional — Cues that direct attention or movement toward a target, location, or "
                    "action. Example: 'Look up.' / 'Move to the right side of the board.'\n\n"
                    "positive_reinforcement — Praise or rewarding feedback given after a correct or "
                    "desired response. Example: 'Yes! That's exactly right.'\n\n"
                    "gaze_cue — Using eye gaze or visual attention cues to guide the participant toward "
                    "something. Example: 'Eyes here.' / 'Look at the board.'\n\n"
                    "physical — Direct physical assistance or intervention beyond simple hand guidance. "
                    "Example: facilitator physically supports the arm or repositions the body.\n\n"
                    "regulation — Prompts aimed at helping the participant regulate emotions, attention, "
                    "or behavior. Example: 'Take a breath.' / 'Slow down and reset.'\n\n"
                    "focus — Prompts intended to regain or maintain the participant's attention on the "
                    "task. Example: 'Stay with me.' / 'Back to the board.'\n\n"
                    "Return at least one label per prompt. Multiple labels are common (e.g., a question "
                    "with directional cues → ['question', 'directional']; praise that also encourages "
                    "continuation → ['positive_reinforcement', 'encouragement']).\n\n"

                    "Return ONLY a JSON array. Each object must contain:\n"
                    "- timestamp — from the transcript\n"
                    "- prompt_text — the facilitator's exact words\n"
                    "- method — one of: s2c, rpm\n"
                    "- type — must come from the vocabulary that matches `method`:\n"
                    "    if method=s2c → one of: initiation, continuation, gesture, direction, none\n"
                    "    if method=rpm → one of: choice, clarification, guided, open_ended, reinforcement\n"
                    "- diwakar_labels — JSON array of one or more of: encouragement, dictation, "
                    "instruction, stm, question, hands, directional, positive_reinforcement, gaze_cue, "
                    "physical, regulation, focus\n\n"
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
    return _extract_json(raw)
