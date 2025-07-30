from .graph_query import get_user_social_context
from .prompt_builder import build_prompt
from .agent import get_suggestions
from .cache import get_cached_suggestions, set_cached_suggestions
from .suggest.suggest_friends import suggest_friends as suggest_fof_graph

import re


def parse_ai_response(response: str) -> list:
    suggestions = []
    lines = response.split("\n")
    for line in lines:
        match = re.match(r"-?\s*(User)?\s*([\w-]{8,})", line.strip())
        if match:
            suggestions.append({"user_id": match.group(2)})
    return suggestions


def suggest_friends_ai(user_id: str) -> list:
    cached = get_cached_suggestions(user_id)
    if cached:
        return cached

    context = get_user_social_context(user_id)
    if not context:
        return []

    prompt = build_prompt(user_id, context)
    ai_response = get_suggestions(prompt)

    suggestions = parse_ai_response(ai_response)
    set_cached_suggestions(user_id, suggestions)

    return suggestions


def suggest_friends_graph(user_id: str, limit: int = 10) -> list:
    return suggest_fof_graph(user_id, limit)
