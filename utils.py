import json


def load_settings():
    with open("settings.json", "r") as f:
        settings = json.load(f)
    return settings
