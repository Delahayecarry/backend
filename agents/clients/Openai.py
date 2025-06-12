from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")

class OpenaiClient:
    def __init__(self,
                 api_key: str = api_key,
                 base_url: str = base_url,
                 model: str = model
                 ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    async def acall(self, prompt: str, model: str = model) -> str:
        """异步调用 OpenAI API"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LLM Error: {str(e)}]"