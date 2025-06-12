import requests

def fetch_real_time_info(query):
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
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()["results"][0]["content"]



    