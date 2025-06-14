from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily

model_info = {
    "family": ModelFamily.UNKNOWN,
    "vision": False,
    "function_calling": True,
    "json_output": False,
    "structured_output": False,
}

class OpenaiForAssistant(OpenAIChatCompletionClient):
    def __init__(self, api_key: str, base_url: str, model: str):
        super().__init__(api_key=api_key, base_url=base_url, model=model, model_info=model_info)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
