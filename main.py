import asyncio
from agents.baseAgent import BaseAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

async def main():
    agent = BaseAgent(name="base_agent", description="A base agent")

    response = await agent.on_messages(
        messages=[TextMessage(content="你知道世界上最深的湖泊是哪个吗？", source="user")],
        cancellation_token=CancellationToken()
    )

    print("Agent Response:", response.chat_message.content)

if __name__ == "__main__":
    asyncio.run(main())
