"""Simple config for EvalX demo."""

class Config:
    def __init__(self):
        self.settings = {"default_llm_model": "gpt-3.5-turbo"}
    
    def get(self, key, default=None):
        return self.settings.get(key, default)

config = Config()
