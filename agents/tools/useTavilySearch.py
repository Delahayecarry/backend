import requests
import os
from dotenv import load_dotenv

# 加载环境变量,但是.env 文件在项目根目录下，所以需要指定路径
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


def fetch_real_time_info(query: str) -> str:
    '''
    搜索工具，用于搜索互联网上的信息
    Args:
        query: 搜索关键词
    Returns:
        搜索结果
    '''
    # 参数
    url = "https://api.tavily.com/search"

    payload = {
        "query": query,
        "topic": "general",
        "search_depth": "basic",
        "chunks_per_source": 3,
        "max_results": 1,
        "time_range": None,
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('TAVILY_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()["results"][0]["content"]



    