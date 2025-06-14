from autogen_agentchat.ui import Console
from autogen_agentchat.base import Team
from autogen_agentchat.agents import AssistantAgent
from agents.clients.OpenaiForAss import OpenaiForAssistant
import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from agents.tools.AllTools import tools



termination = MaxMessageTermination(max_messages=10)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL") # 确保这个变量在全局可用，或者作为类属性传递

model_client = OpenaiForAssistant(api_key=api_key, base_url=base_url, model=model)

agent1 = AssistantAgent(
    name="agent1",
    model_client=model_client,
    tools=tools,
)
agent2 = AssistantAgent(
    name="agent2",
    model_client=model_client,
)

agent3 = AssistantAgent(
    name="agent3",
    model_client=model_client,
)

async def main():
    team = RoundRobinGroupChat(participants=[agent1, agent2, agent3], termination_condition=termination)
    task = "世界上最长的河流是什么？计算它的长度和第二长的长度的差是多少？"
    await Console(team.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())