from functools import lru_cache


@lru_cache(maxsize=1000)
def get_cached_suggestions(user_id: str):
    return None  # Replace with actual if persistent


def set_cached_suggestions(user_id: str, suggestions: list):
    pass  # Optionally write to Redis or DB
