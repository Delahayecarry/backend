from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os




class openaiForAssistant(OpenAIChatCompletionClient):
    def __init__(self, api_key: str, base_url: str, model: str):
        super().__init__(api_key=api_key, base_url=base_url, model=model)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url