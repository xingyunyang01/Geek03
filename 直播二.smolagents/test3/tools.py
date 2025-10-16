import datetime
import hashlib
import json
import os
import time
import requests

from smolagents import Tool

from dotenv import load_dotenv

load_dotenv()

def bochasearch(query:str,page:int=1,pagesize:int=5,sites:str="*"):
    bochakey=os.environ["BOCHA_API_KEY"]
    ep="https://api.bochaai.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {bochakey}",
        "Content-Type": "application/json"
    }
    data={
        "query":query,
        "summary":True,
        "count":pagesize,
        "include": sites,
        "page":page
    }
    response = requests.post(ep,
                             data=json.dumps(data),
                             headers=headers)
    try:
        return response.json()
    except Exception as e:
        return  {"error":str(e)}

def bocha_for_list(query:str,page:int=1,pagesize:int=5,
                            sites:str="*"):
     search_ret=bochasearch(query,page,pagesize,sites)
     data=search_ret["data"]
     pages=data["webPages"]["value"]

     results = [
         {
             "title": page["name"],
             "link": page["url"],
             "description": page["summary"],
         }
         for page in pages
     ]
     return results


#pip install goose3[chinese]  这是一个通用的网页解析库  可以获取文字 (js格式的不可以)
from goose3 import Goose
from goose3.text import StopWordsChinese
async def fetch_url(url:str,max_length:int=500):
    g = Goose({'stopwords_class': StopWordsChinese,
               'browser_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    try:
        article = g.extract(url=url)
        if article==None or article.cleaned_text==None:
            return f"{url}目前不可用,请查看其他信息"
        # print(article.title)
        return article.cleaned_text[:max_length]
    except Exception as e:
        return f"{url}目前不可用,请查看其他信息"

class BochaSearchTool(Tool):
    name = "web_search"
    description = "Performs a web search for a query and returns a string of the top search results formatted as markdown with titles, links, and descriptions."
    inputs = {"query": {"type": "string", "description": "The search query to perform."}}
    output_type = "string"

    def __init__(self, max_results: int = 10, engine: str = "duckduckgo"):
        super().__init__()
        self.max_results = max_results
        self.engine = engine

    def forward(self, query: str) -> str:
        results = self.search(query)
        if len(results) == 0:
            raise Exception("No results found! Try a less restrictive/shorter query.")
        return self.parse_results(results)

    def search(self, query: str) -> list:
         return bocha_for_list(query)
    def parse_results(self, results: list) -> str:
        return "## Search Results\n\n" + "\n\n".join(
            [f"[{result['title']}]({result['link']})\n{result['description']}" for result in results]
        )