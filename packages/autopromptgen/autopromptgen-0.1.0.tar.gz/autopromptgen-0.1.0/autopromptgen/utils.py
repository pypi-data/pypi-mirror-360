import os
import json

def load_templates():
    filepath = os.path.join(os.path.dirname(__file__), "templates", "prompt_templates.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}
