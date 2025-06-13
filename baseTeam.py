from autogen_agentchat import agents
from agents import BaseAgent
from agents.tools import *
from agents.clients import openaiForAssistant, OpenaiClient
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
import asyncio
from dotenv import load_dotenv
import os
# 获取环境变量
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL") # 确保这个变量在全局可用，或者作为类属性传递

testagent = BaseAgent(
    name="testagent",
    model_client=OpenaiClient(api_key=api_key, base_url=base_url, model=model),
    handoffs=["assistant_agent", "user"]
)

assistant_agent = agents.AssistantAgent(
    name="assistant_agent",
    model_client=openaiForAssistant(api_key=api_key, base_url=base_url, model=model),
    description="You are a helpful assistant.",
    tools=[fetch_real_time_info, calculate],
    handoffs=["testagent", "user"]
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([testagent, assistant_agent], termination_condition=termination)
task = "世界上最长的河流是什么？计算它的长度和第二长的长度的差是多少？"

async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]


async def main() -> None:
    await run_team_stream()
    await assistant_agent._model_client.close()

if __name__ == "__main__":
    asyncio.run(main())