from . import config
from neo4j import GraphDatabase


class GraphClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )

    def run_query(self, query, params):
        with self.driver.session() as session:
            return session.run(query, params).data()

    def close(self):
        self.driver.close()


def get_user_social_context(user_id: str) -> list:
    driver = GraphDatabase.driver(
        config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    with driver.session() as session:
        result = session.run(
            """
            MATCH (me:User {id: $user_id})-[:FRIEND]->(friend:User)
            OPTIONAL MATCH (friend)-[:FRIEND]->(foaf:User)
            OPTIONAL MATCH (foaf)-[:GOING_TO|:RSVP|:ATTENDED]->(event:Event)
            RETURN friend.id AS friend_id,
                   collect(DISTINCT foaf.id) AS foaf_ids,
                   collect(DISTINCT event.id) AS shared_event_ids
        """,
            {"user_id": user_id},
        )
        records = result.data()
    driver.close()
    return records


__all__ = ["GraphClient", "get_user_social_context"]
