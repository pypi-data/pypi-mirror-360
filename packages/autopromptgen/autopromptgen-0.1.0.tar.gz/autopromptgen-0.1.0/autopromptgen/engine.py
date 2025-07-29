import random
from .utils import load_templates

class PromptGenerator:
    def __init__(self):
        self.templates = load_templates()

    def generate_prompt(self, category="general", user_input=""):
        prompts = self.templates.get(category, [])
        if not prompts:
            return f"No templates found for category: {category}"
        prompt = random.choice(prompts)
        return prompt.replace("{input}", user_input if user_input else "your task")
