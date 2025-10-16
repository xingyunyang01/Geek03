import datetime
import hashlib
import json
import os
import time
import requests

from smolagents import Tool
import akshare as ak
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

from httphelper import get_html

data_root="/root/python/smolagents/files/data"
def find_csv():
    csvdir=data_root
    # 查找csvdir目录下的所有CSV文件,并取出最新的一个
    csv_files = [f for f in os.listdir(csvdir) if f.endswith('.csv')]
    if not csv_files:
        return None
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(csvdir, x)))
    return os.path.join(csvdir, csv_files[-1])
import pandas as pd
def set_ma(df:pd.DataFrame,to_file:str=""):
    df['ma5'] = df.groupby('股票代码')['收盘']. \
        rolling(window=5).mean().shift(-4).reset_index(0, drop=True)
    df['ma10'] = df.groupby('股票代码')['收盘']. \
        rolling(window=10).mean().shift(-9).reset_index(0, drop=True)
    df['ma20'] = df.groupby('股票代码')['收盘']. \
        rolling(window=20).mean().shift(-19).reset_index(0, drop=True)
    df['ma30'] = df.groupby('股票代码')['收盘']. \
        rolling(window=30).mean().shift(-29).reset_index(0, drop=True)
    df['ma60'] = df.groupby('股票代码')['收盘']. \
        rolling(window=60).mean().shift(-59).reset_index(0, drop=True)
    df['ma5'] = df['ma5'].round(2)
    df['ma10'] = df['ma10'].round(2)
    df['ma20'] = df['ma20'].round(2)
    df['ma30'] = df['ma30'].round(2)
    df['ma60'] = df['ma60'].round(2)
    if to_file!=None and to_file!="":
        df.to_csv(f"{data_root}/{to_file}",index=False)
        print("保存文件完成,文件名是:{}".format(to_file))

def get_symbol(input:str):
    input=input.lower()
    if "sz" in input:
        input=input.replace("sz","")
    if  "sh" in input:
        input=input.replace("sh","")

    if input.isdigit(): #直接就是  股票代码
        return input
    else:
        df=ak.stock_zh_a_spot_em()
        df=df[df["名称"].str.contains(input)]
        return df["代码"].values[0]

class GetKlineData(Tool):
    name = "KlineData_tool"
    description = "获取股票K线数据,支持日K、周K和月K"
    inputs = {"codeorname":{"type": "string",
                            "description": "股票代码或股票名称"},
              "period":{
                  "type": "string",
                  "description": "3个选项选其一:daily、weekly或monthly,分表代表日K、周K和月K",
               },
              "start_date": {
                  "type": "string",
                  "description": "起始日期,示例:'20250301'",
              },
              "end_date": {
                  "type": "string",
                  "description": "结束日期,示例:'20250401'",
              },
            }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, codeorname: str, period:str, start_date: str , end_date: str) -> pd.DataFrame:
        csvfile = find_csv()
        df = pd.read_csv(csvfile, dtype={'股票代码': str})
        set_ma(df)
        df['日期'] = pd.to_datetime(df['日期'])

        start_date = start_date.replace("-", "")
        end_date = end_date.replace("-", "")
        # 如果start_date和end_date为空 ，则往前推一周
        if start_date == "" or end_date == "":
            end_date = datetime.datetime.now().strftime("%Y%m%d")
            start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y%m%d")
        symbol = get_symbol(codeorname)
        df = ak.stock_zh_a_hist(symbol=symbol,
                                period=period,
                                start_date=start_date,
                                end_date=end_date, adjust="qfq")
        return df

class GetCjNews(Tool):
    name = "CjNews_tool"
    description = "获取最新的财经新闻"
    inputs={}
    output_type = "object"

    def __init__(self):
        super().__init__()

    def get_cjnews(self,page=1):
        url = f"https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=350&order=1&needInteractData=0&page_index={page}&page_size=50&req_trace=1750600308076&fields=showTime,title,summary&types=1,20&callback=jQuery"
        html = get_html(url)
        # 替换html开头的jQuery( 字符串
        html = html.lstrip("jQuery(")
        # 替换html结尾的) 字符串,
        html = html.strip(")")

        return html

    def cls_sign(self,url: str):
        def use_md5(input_string):
            # 使用 hashlib 库计算 MD5
            sha1_hash = hashlib.sha1(input_string.encode()).hexdigest()

            # 计算MD5哈希
            md5_hash = hashlib.md5(sha1_hash.encode()).hexdigest()
            return md5_hash
        return use_md5(url)

    def clear_html(self,text):
        replace_strs = ['\n', '\t', '\r', ' ', '\xa0', '\u3000']
        for str in replace_strs:
            text = text.replace(str, '')
        return text

    def get_cls_red_telegram(self) -> str:
        timestamp = int(time.time())
        param_str = "app=CailianpressWeb&category=red&last_time={}&os=web&refresh_type=1&rn=20&sv=8.4.6". \
            format(timestamp)
        sign_str = self.cls_sign(param_str)
        param_str = param_str + "&sign=" + sign_str
        url = "https://www.cls.cn/v1/roll/get_roll_list?{}".format(param_str)

        rsp_text = get_html(url)
        if rsp_text == "":
            return "没有找到数据"
        ret = ""
        jsons = json.loads(rsp_text)
        if 'data' in jsons and 'roll_data' in jsons['data']:
            items = jsons['data']['roll_data']
            for item in items:
                ret += self.clear_html(item['content'])
                ret += "\n\n"
            return ret
        return "没有找到数据"

    def forward(self):
        news_data1 = self.get_cjnews()
        news_data2 = self.get_cls_red_telegram()
        return {
            "财经新闻": news_data1,
            "加红消息": news_data2
        }

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