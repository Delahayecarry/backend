import re
import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import Response
from autogen_core import CancellationToken
from autogen_agentchat.agents import BaseChatAgent, AssistantAgent
from autogen_agentchat.messages import BaseChatMessage
from typing import Sequence, List
from agents.tools.useTavilySearch import fetch_real_time_info
from agents.tools.useCalculator import calculate
from agents.pormpt.parentPrompt import parent_prompt
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import UserMessage, AssistantMessage, FunctionExecutionResultMessage
from autogen_core.models import ChatCompletionClient
action_re = re.compile(r'^Action: (\w+): (.*)$', re.MULTILINE)

class BaseAgent(AssistantAgent):
    def __init__(self, name: str, model_client: ChatCompletionClient, handoffs: List[str]):
        super().__init__(name, model_client, handoffs=handoffs)
        self.available_tools = { 
            "fetch_real_time_info": fetch_real_time_info,
            "calculate": calculate
        }
        self.system_prompt = parent_prompt
        self.model_client = model_client
        self.max_turns = 50
        # 存储上下文
        self._model_context = UnboundedChatCompletionContext()
        # 情感模型
        self.handoffs = handoffs
        #

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


        
        user_message = messages[-1].content.strip() # 获取用户输入
        await self._model_context.add_message(UserMessage(content=user_message, source="user"))

        print(f"[SYSTEM] Question: {user_message}") # 打印用户输入

        turns = 0 # 初始化轮次
        llm_response = "No response generated"  # 初始化默认值
        
        

        while turns < self.max_turns and not cancellation_token.is_cancelled(): # 如果轮次小于最大轮次且没有取消，则继续循环
            turns += 1 # 轮次加1
            conversation_context = await self._model_context.get_messages() # 获取上下文
            # 调用 LLM
            llm_response = await self.model_client.acall(
                messages=conversation_context,
                system_instruction=self.system_prompt
            )
            print(f"[LLM Response #{turns}]\n{llm_response}\n") # 打印 LLM 响应
            await self._model_context.add_message(AssistantMessage(content=llm_response, source="agent"))
            # 查找 Action 行
            action_match = action_re.search(llm_response)
            if action_match: # 如果找到 Action 行
                action_name, action_input = action_match.groups() # 获取 Action 名称和输入
                tool = self.available_tools.get(action_name) # 获取工具

                if not tool: # 如果工具不存在，则返回错误
                    return Response(chat_message=TextMessage(content=f"[ERROR] Unknown tool: {action_name}", source="agent")) # 如果工具不存在，则返回错误

                print(f"[SYSTEM] Calling tool: {tool}") # 打印工具调用
                try: # 工具调用（同步包装为异步）
                    observation = await asyncio.to_thread(tool, action_input)
                    # 添加观察结果到上下文
                    await self._model_context.add_message(FunctionExecutionResultMessage(tool_name=action_name, result=observation, is_error=True))

                except Exception as e:
                    observation = f"[Tool Error: {str(e)}]"
                    await self._model_context.add_message(FunctionExecutionResultMessage(tool_name=action_name, result=observation))
            else:
                return Response(chat_message=TextMessage(content=llm_response, source="agent"))

        return Response(chat_message=TextMessage(content=llm_response, source="agent"))
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """Reset the assistant by clearing the model context."""
        await self._model_context.clear()
