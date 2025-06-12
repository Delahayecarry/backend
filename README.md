# Multi-AI Agent Framework

## 项目概述

Multi-AI是一个基于AutoGen框架构建的智能代理系统，旨在创建能够执行复杂任务的AI代理。该项目实现了一个具有工具调用能力的基础代理，可以通过ReAct (Reason and Act) 模式与外部工具交互，实现信息检索和数学计算等功能。

## 核心特性

### 🤖 智能代理系统
- 基于AutoGen Chat框架的异步代理实现
- 支持ReAct (Reason, Action, Observation) 推理模式
- 可扩展的工具调用架构

### 🔧 内置工具集
- **实时信息检索**: 集成Tavily搜索API，获取最新网络信息
- **数学计算器**: 支持复杂数学表达式计算
- **可扩展工具接口**: 轻松添加新的工具和功能

### 🌐 LLM集成
- OpenAI API集成，支持自定义模型和API端点
- 异步调用机制，提高响应效率
- 可配置的模型参数和环境变量管理

## 项目架构

```
backend/
├── main.py                 # 主程序入口
├── agents/                 # 代理模块
│   ├── baseAgent.py       # 基础代理类
│   ├── clients/           # LLM客户端
│   │   └── Openai.py      # OpenAI客户端实现
│   ├── tools/             # 工具集
│   │   ├── useTavilySearch.py  # 搜索工具
│   │   └── useCalculator.py    # 计算工具
│   └── pormpt/            # 提示词模板
│       └── basePrompt.py  # 基础提示词
├── pyproject.toml         # 项目配置
└── README.md              # 项目文档
```

## 技术栈

- **Python 3.10+**: 主要编程语言
- **AutoGen**: AI代理框架
- **OpenAI API**: 大语言模型服务
- **Tavily API**: 实时搜索服务
- **AsyncIO**: 异步编程支持

## 快速开始

### 环境要求
- Python 3.10+
- UV包管理器 (推荐) 或 pip

### 安装依赖

```bash
# 使用UV (推荐)
uv sync

# 或使用pip
pip install -r requirements.txt
```

### 环境配置

创建`.env`文件并配置以下环境变量：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，默认官方API
OPENAI_MODEL=gpt-3.5-turbo  # 可选，默认模型

# Tavily搜索API (可选)
TAVILY_API_KEY=your_tavily_api_key
```

### 运行示例

```bash
python main.py
```

## 使用示例

### 基础问答
```python
import asyncio
from agents.baseAgent import BaseAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

async def main():
    agent = BaseAgent(name="assistant", description="智能助手")
    
    response = await agent.on_messages(
        messages=[TextMessage(content="计算 15 * 23 + 45", source="user")],
        cancellation_token=CancellationToken()
    )
    
    print("回答:", response.chat_message.content)

asyncio.run(main())
```

### ReAct推理示例
代理将自动识别需要使用的工具：

**用户输入**: "2024年世界杯在哪里举办？"
**代理推理过程**:
1. **Thought**: 我需要搜索2024年世界杯的信息
2. **Action**: fetch_real_time_info: 2024年世界杯举办地点
3. **Observation**: [搜索结果]
4. **Answer**: 基于搜索结果的回答

## 核心组件说明

### BaseAgent
- 继承自AutoGen的`BaseChatAgent`
- 实现ReAct推理循环
- 支持多轮对话和工具调用
- 内置错误处理和超时机制

### 工具系统
- **fetch_real_time_info**: 使用Tavily API进行实时网络搜索
- **calculate**: 安全的数学表达式计算器
- 可通过`available_tools`字典轻松扩展新工具

### OpenAI客户端
- 支持异步调用
- 可配置的API端点和模型参数
- 完整的错误处理机制

## 开发指南

### 添加新工具
1. 在`agents/tools/`目录下创建新的工具文件
2. 实现工具函数，接受字符串参数，返回字符串结果
3. 在`BaseAgent`的`available_tools`中注册工具
4. 更新系统提示词以包含工具描述

### 自定义代理
```python
class CustomAgent(BaseAgent):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        # 添加自定义工具
        self.available_tools["custom_tool"] = your_custom_tool
        # 自定义系统提示词
        self.system_prompt = your_custom_prompt
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

### 开发环境设置
```bash
git clone [repository-url]
cd Multi-ai/backend
uv sync
```

### 代码规范
- 遵循PEP 8代码风格
- 为新功能添加文档字符串
- 编写单元测试（推荐）

## 许可证

本项目采用 [LICENSE] 许可证。

## 更新日志

### v0.1.0
- 初始版本发布
- 实现基础代理和工具调用系统
- 集成OpenAI和Tavily API
- 支持ReAct推理模式

---

**注意**: 请确保妥善保管您的API密钥，不要将其提交到版本控制系统中。
