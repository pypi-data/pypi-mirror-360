"""Configuration for Neo4j and OpenAI keys."""

import os

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def set_config(**kwargs):
    global NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_KEY
    for key, value in kwargs.items():
        if key in globals():
            globals()[key] = value
