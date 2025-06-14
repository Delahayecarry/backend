# agents/clients/Openai.py

from dotenv import load_dotenv
import os
import asyncio
from typing import List, Optional
from autogen_agentchat.messages import BaseChatMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage, AssistantMessage, SystemMessage
# 导入 Autogen 结构化消息类型
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL") # 确保这个变量在全局可用，或者作为类属性传递

class OpenaiClient(OpenAIChatCompletionClient):
    def __init__(self,
                 api_key: str = api_key,
                 base_url: str = base_url,
                 model: str = model, # 将模型作为初始化参数或直接在 acall 中使用 
                 **kwargs):
        super().__init__(
            api_key=api_key, 
            base_url=base_url, 
            model=model,
            **kwargs
            )
        self.model = model
        # OpenAIChatCompletionClient 内部会处理 OpenAI 客户端的初始化
        # 不需要直接访问 self.client。OpenAIChatCompletionClient 本身就是客户端接口。

    # 修改 acall 函数签名，接收 messages 列表和可选的 system_instruction
    async def acall(self, messages: List[BaseChatMessage], system_instruction: Optional[str] = None) -> str:
        """
        异步调用 OpenAI API，接收 Autogen 结构化消息列表作为对话历史。
        """
        openai_messages = []

        # 1. 首先处理系统指令 (如果存在)
        if system_instruction:
            openai_messages.append({"role": "system", "content": system_instruction})

        # 2. 遍历 Autogen 的 BaseMessage 列表，将其转换为 OpenAI API 期望的格式
        for msg in messages:
            if isinstance(msg, UserMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AssistantMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                # 如果 system_instruction 已经处理了系统消息，这里可以跳过
                # 否则，如果 _model_context 中有 SystemMessage，也可以添加到这里
                # 确保不与 system_instruction 重复
                openai_messages.append({"role": "system", "content": msg.content})
            else:
                # 处理其他未知或未映射的 Autogen 消息类型
                # 简单地将其内容作为用户消息添加
                openai_messages.append({"role": "user", "content": str(msg.content)})

        # 确保消息列表不为空，否则 OpenAI API 会报错
        if not openai_messages:
            return "[LLM Error: No messages to send to OpenAI API]"

        try:
            # 这里的关键是：
            # 1. OpenAIChatCompletionClient 应该提供一个同步的 'create' 方法。
            # 2. 我们使用 asyncio.to_thread 将其转换为异步调用。
            response = await asyncio.to_thread(
                self.create, # 调用父类的同步 create 方法
                messages=openai_messages,
            )
            # Autogen 客户端的 create 方法返回的对象通常与 OpenAI API 的原始响应结构相似

            return response.message.content.strip()
        except Exception as e:
            # 捕获并返回 LLM 错误
            return f"[LLM Error: {str(e)}]"