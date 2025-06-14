import asyncio
from agents.baseAssistant import BaseAssistant
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from agents.clients.OpenaiForAss import OpenaiForAssistant
from dotenv import load_dotenv
import os
from agents.pormpt.basePrompt import system_prompt
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")

user_message = """
你的任务：

请让你的代理找出以下信息，并进行计算：

搜索：

查找 中国 的最新总人口（近似值即可，例如 2023 或 2024 年的数据）。
查找 美国 的最新总人口（近似值，例如 2023 或 2024 年的数据）。
查找 中国 的国土面积（精确到平方公里）。
查找 美国 的国土面积（精确到平方公里）。
计算：

计算 中国 的人口密度（每平方公里人口数），结果保留两位小数。
计算 美国 的人口密度（每平方公里人口数），结果保留两位小数。
计算 中国和美国 的总人口。
计算 中国和美国 的总国土面积。
最终答案：

总结以上所有数据和计算结果，清晰地呈现。
强调哪个国家的人口密度更高。
"""


async def main():
    agent = BaseAssistant(name="base_agent", model_client=OpenaiForAssistant(api_key=api_key, base_url=base_url, model=model), handoffs=["user"], system_prompt=system_prompt)

    response = await agent.on_messages(
        messages=[TextMessage(content=user_message, source="user")],
        cancellation_token=CancellationToken()
    )

    print("Agent Response:", response.chat_message.content)

if __name__ == "__main__":
    asyncio.run(main())
