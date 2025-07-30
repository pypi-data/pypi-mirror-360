def build_prompt(user_id: str, context_data: list) -> str:
    prompt = [f"User {user_id} has the following social graph:\n"]

    for entry in context_data:
        foafs = ", ".join(entry["foaf_ids"] or [])
        events = ", ".join(entry["shared_event_ids"] or [])
        prompt.append(
            f"Friend {entry['friend_id']} → Friends: [{foafs}] → Events: [{events}]"
        )

    prompt.append(
        "\nBased on this graph, suggest 3 friends of friends that this user might want to connect with. Only suggest users who are not already friends."
    )
    return "\n".join(prompt)
