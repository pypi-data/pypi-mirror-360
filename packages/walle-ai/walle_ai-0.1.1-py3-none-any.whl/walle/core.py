from .graph_query import get_user_social_context
from .prompt_builder import build_prompt
from .agent import get_suggestions
from .cache import get_cached_suggestions, set_cached_suggestions


def suggest_friends(user_id: str) -> list:
    cached = get_cached_suggestions(user_id)
    if cached:
        return cached

    context = get_user_social_context(user_id)
    if not context:
        return []

    prompt = build_prompt(user_id, context)
    ai_response = get_suggestions(prompt)

    suggestions = [{"raw": ai_response}]
    set_cached_suggestions(user_id, suggestions)

    return suggestions
