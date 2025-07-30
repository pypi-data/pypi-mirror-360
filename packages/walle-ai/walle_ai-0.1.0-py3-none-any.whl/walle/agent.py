import openai
from .config import OPENAI_KEY

openai.api_key = OPENAI_KEY


def get_suggestions(prompt: str) -> list:
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You suggest friends based on social networks.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=300,
    )
    return response.choices[0].message["content"]
