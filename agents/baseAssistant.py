import re
import asyncio  
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import BaseChatMessage
from typing import Sequence, List
from autogen_core.models import AssistantMessage, ChatCompletionClient



# 导入您的工具
from backend.agents.tools.AllTools import tools



# action_re = re.compile(r'^Action:\s*(\w+)\s*:\s*(.*)$', re.MULTILINE | re.DOTALL)


class BaseAssistant(AssistantAgent):
    def __init__(self, name: str, model_client: ChatCompletionClient, handoffs: List[str], system_prompt: str):
        super().__init__(
            name=name,
            handoffs=handoffs,
            model_client=model_client,
            tools=tools
        )
        self.model_client = model_client
        self.max_turns = 50
        self.conversation_context = []


    async def on_messages(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token: CancellationToken
    ) -> Response:
        for msg in messages:
            await self._model_context.add_message(msg)
        self.conversation_context.extend(messages)

        if not messages:
            return Response(messages=[TextMessage(content="没有收到输入。", source="agent")])
        

        user_message = messages[-1].content.strip() # 获取用户消息
        print(f"[系统] 问题: {user_message}")

        turns = 0 # 轮次


        while turns < self.max_turns and not cancellation_token.is_cancelled(): # 如果轮次小于最大轮次且没有取消，则继续循环
            turns += 1 # 轮次加1
            conversation_context = await self._model_context.get_messages() # 获取上下文
            # 调用 LLM
            llm_response = await self.model_client.create(
                messages=conversation_context,
                tools=tools
            )
            print(f"[LLM Response #{turns}]\n{llm_response}\n") # 打印 LLM 响应
            await self._model_context.add_message(AssistantMessage(content=llm_response.content, source="agent"))

        return Response(chat_message=TextMessage(content=llm_response.message.content, source="agent"))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """Reset the agent by clearing its internal chat context."""
        await self.clear_chat_context() # 使用 AssistantAgent 的内置方法