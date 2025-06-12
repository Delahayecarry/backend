import re
import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import BaseChatMessage
from typing import Sequence
from agents.tools.useTavilySearch import fetch_real_time_info
from agents.tools.useCalculator import calculate
from agents.clients.Openai import OpenaiClient
from agents.pormpt.parentPrompt import parent_prompt
from autogen_core.model_context import UnboundedChatCompletionContext

action_re = re.compile(r'^Action: (\w+): (.*)$', re.MULTILINE)

class BaseAgent(BaseChatAgent):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.llmClient = OpenaiClient()
        self.available_tools = { 
            "fetch_real_time_info": fetch_real_time_info,
            "calculate": calculate
        }
        self.system_prompt = parent_prompt
        self.max_turns = 50
        # 存储上下文
        self._model_context = UnboundedChatCompletionContext()

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

    async def on_messages(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token: CancellationToken
    ) -> Response:
        if not messages: #如果用户没有输入，则返回错误
            return Response(messages=[TextMessage(content="No input received.", source="agent")])

        # 添加用户消息到上下文
        self._model_context.add_message(messages[-1].content)

        question = messages[-1].content.strip() # 获取用户输入
        next_prompt = f"{self.system_prompt}\nQuestion: {question}" # 构建提示词
        turns = 0 # 初始化轮次
        llm_response = "No response generated"  # 初始化默认值
        
        print(f"[SYSTEM] Question: {question}") # 打印用户输入

        while turns < self.max_turns and not cancellation_token.is_cancelled(): # 如果轮次小于最大轮次且没有取消，则继续循环
            turns += 1 # 轮次加1

            llm_response = await self.llmClient.acall(next_prompt) # 调用 LLM（等价于 bot(next_prompt)）
            print(f"[LLM Response #{turns}]\n{llm_response}\n") # 打印 LLM 响应

            # 查找 Action 行
            action_match = action_re.search(llm_response)
            if action_match:
                action_name, action_input = action_match.groups()

                tool = self.available_tools.get(action_name)

                if not tool:
                    return Response(chat_message=TextMessage(content=f"[ERROR] Unknown tool: {action_name}", source="agent")) # 如果工具不存在，则返回错误

                print(f"[SYSTEM] Calling tool: {tool}") # 打印工具调用
                try:
                    observation = await asyncio.to_thread(tool, action_input) # 工具调用（同步包装为异步）

                except Exception as e:
                    observation = f"[Tool Error: {str(e)}]"

                # 保持完整上下文，添加观察结果
                next_prompt = f"\nObservation: {observation}"
            else:
                return Response(chat_message=TextMessage(content=llm_response, source="agent"))

        return Response(chat_message=TextMessage(content=llm_response, source="agent"))
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """Reset the assistant by clearing the model context."""
        await self._model_context.clear()
