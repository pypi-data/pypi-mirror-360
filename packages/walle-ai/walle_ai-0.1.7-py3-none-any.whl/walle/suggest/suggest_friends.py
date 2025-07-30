from ..graph_query import GraphClient


def suggest_friends(user_id: str, limit: int = 10) -> list:
    query = """
        MATCH (user:User {id: $user_id})-[:FRIEND]->(friend:User)-[:FRIEND]->(fof:User)
        WHERE NOT (user)-[:FRIEND]->(fof) AND user <> fof
        RETURN fof.id AS suggested_user_id, COUNT(DISTINCT friend) AS mutual_friend_count
        ORDER BY mutual_friend_count DESC
        LIMIT $limit
    """
    client = GraphClient()
    result = client.run_query(query, {"user_id": user_id, "limit": limit})
    client.close()

    suggestions = [
        {
            "user_id": record["suggested_user_id"],
            "mutuals": record["mutual_friend_count"],
        }
        for record in result
    ]
    return suggestions
