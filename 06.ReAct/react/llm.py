import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

client = OpenAI(
    api_key=os.getenv("TONGYI_API_KEY"),  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)