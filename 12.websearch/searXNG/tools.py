import json
import os

import requests
from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import tool

@tool
async def widesearch_for_toolstr(query:str):
    """
    使用searx搜索工具进行网络搜索。
    参数:
        query (str): 搜索查询字符串。
    返回:
        str: 搜索结果的markdown格式化字符串，每个结果包含标题、简介和链接。
    """

    print(f"搜索查询字符串: {query}")
    
    engines = ["baidu", "sogou", "quark"]
    search = SearxSearchWrapper(
        searx_host="your_searx_host",
    )  # k用于最大项目数
    search_ret = search.results(query, num_results=5,
                         time_range="year",
                         engines=engines)
    strtemplate = """
    标题:{}
    简介:{}
    链接:{}

    """

    ret = ""
    for data in search_ret:
        # 安全地获取字段值，如果不存在则使用默认值
        title = data.get("title", "无标题")
        snippet = data.get("snippet", "无简介")
        link = data.get("link", "无链接")

        ret += strtemplate.format(title, snippet, link)
    return ret

tools = [widesearch_for_toolstr]
tools_by_name = {tool.name: tool for tool in tools}