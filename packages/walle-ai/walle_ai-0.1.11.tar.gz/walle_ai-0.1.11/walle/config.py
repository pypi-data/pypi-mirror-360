import os


NEO4J_URI = None
NEO4J_USER = None
NEO4J_PASSWORD = None
OPENAI_KEY = None


def set_config(**kwargs):
    global NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_KEY
    for key, value in kwargs.items():
        if key in globals():
            globals()[key] = value
