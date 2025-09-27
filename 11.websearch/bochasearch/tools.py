import json
import os

import requests

async def bochasearch(query:str, page:int=1, pagesize:int=5):
    bochakey=os.environ.get("BOCHA_API_KEY")
    ep="https://api.bochaai.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {bochakey}",
        "Content-Type": "application/json"
    }
    data={
        "query":query,
        "summary":True,
        "count":pagesize,
        "page":page
    }
    response = requests.post(ep,
                             data=json.dumps(data),
                             headers=headers)
    try:
        return response.json()
    except Exception as e:
        return  {"error":str(e)}

# 查询到内容后 调用fetch_url 拼接成 字符串
async def bocha_for_detail(query: str,chunck_size:int=200):
    search_ret = await bochasearch(query)
    data = search_ret["data"]
    pages = data["webPages"]["value"]
    strtemplate = """
标题:{}
内容:{}

    """
    ret = ""
    for page in pages:
        page_detail=await fetch_url(page["url"],chunck_size)
        ret += strtemplate.format(page["name"], page_detail)
    return ret

#将搜索结果拼接成列表
async def bocha_for_list(query: str):
    search_ret = await bochasearch(query)
    data = search_ret["data"]
    pages = data["webPages"]["value"]
    ret=[]
    for page in pages:
        ret.append({"title":page["name"],"summary":page["summary"],"url":page["url"]})
    return ret

#将搜索结果拼接成字符串
async def bocha_for_toolstr(query:str):
     search_ret=await bochasearch(query)
     data=search_ret["data"]
     pages=data["webPages"]["value"]
     strtemplate="""
标题:{}
简介:{}
链接:{}

"""

     ret=""
     for page in pages:
         ret+=strtemplate.format(page["name"],page["summary"],page["url"])
     return ret

#pip install goose3[chinese]  这是一个通用的网页解析库  可以获取文字 (js格式的不可以)
from goose3 import Goose
from goose3.text import StopWordsChinese
async def fetch_url(url:str,max_length:int=500):
    g = Goose({'stopwords_class': StopWordsChinese,
               'browser_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    article = g.extract(url=url)
    # print(article.title)
    return article.cleaned_text[:max_length]