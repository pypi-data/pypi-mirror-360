from openai import OpenAI
from . import config

from functools import lru_cache


@lru_cache(maxsize=1)
def get_client():
    return OpenAI(api_key=config.OPENAI_KEY)


def get_suggestions(prompt: str) -> str:
    response = get_client().chat.completions.create(
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
    return response.choices[0].message.content
