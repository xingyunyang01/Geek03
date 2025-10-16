from typing import List
from pydantic import BaseModel, Field
from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import tool
import os
import json
import requests

class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="用于web搜索的查询信息列表"
    )
    rationale: str = Field(
        description="简要说明为什么这些查询与research主题相关。"
    )

class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="是否提供了足够的信息来回答用户的问题。"
    )
    knowledge_gap: str = Field(
        description="描述缺少或需要澄清的信息。"
    )
    follow_up_queries: List[str] = Field(
        description="用于解决知识差距的后续查询列表。"
    )


@tool
def widesearch_for_toolstr(query:str):
    """
    使用searx搜索工具进行网络搜索。
    参数:
        query (str): 搜索查询字符串。
    返回:
        str: 搜索结果的markdown格式化字符串，每个结果包含标题、简介和链接。
    """
    engines = ["baidu", "sogou", "quark"]
    search = SearxSearchWrapper(
        searx_host="http://116.153.88.164:18080/",
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