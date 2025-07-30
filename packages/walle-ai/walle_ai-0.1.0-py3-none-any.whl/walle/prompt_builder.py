def build_prompt(user_id: str, context_data: list) -> str:
    prompt = [f"User ID {user_id} has the following network:\n"]

    for entry in context_data:
        foafs = ", ".join(entry["foaf_ids"] or [])
        events = ", ".join(entry["shared_event_ids"] or [])
        prompt.append(
            f"- Friend {entry['friend_id']} is connected to [{foafs}] and attended [{events}]"
        )

    prompt.append("\nBased on this, suggest 3 users to connect with.")
    return "\n".join(prompt)
