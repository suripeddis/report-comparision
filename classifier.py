import os
from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()



client = OpenAI(api_key=os.environ.get("OPEN_API_KEY"))

def classify_ask_type(text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are classifying therapy session questions.\n"
                    "Classify the question into exactly ONE of these labels:\n"
                    "- Open-ended\n"
                    "- Recall\n"
                    "- Sentence generation\n"
                    "- Yes/No\n"
                    "- Binary choice\n"
                    "- Multiple choice\n"
                    "- Invite speller questions\n"
                    "- Other/Unclear\n\n"
                    "Return ONLY the label. No explanation."
                )
            },
            {
                "role": "user",
                "content": f"Question: {text}"
            }
        ]
    )

    return response.choices[0].message.content.strip()

