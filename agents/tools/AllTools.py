from .useTavilySearch import fetch_real_time_info
from autogen_core.tools import FunctionTool
from .useCalculator import calculate    
# 要求为字典


# 应该是一个列表，列表中包含字典
tools = [
    FunctionTool(
        fetch_real_time_info,
        name="fetch_real_time_info",
        description="can use to search real time info from tavily api"
        # FunctionTool 会自动从 fetch_real_time_info 的函数签名中提取参数
        # 如果函数本身没有参数，或者您希望更精细控制，需要查看 FunctionTool 的文档
    ),
    FunctionTool(
        calculate,
        name="calculate",
        description="can use to calculate the result of a math expression"
        # 同上，参数会自动提取
    )
]