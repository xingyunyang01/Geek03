import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

# 加载 .env 文件
load_dotenv()

def DeepSeek():
    return ChatDeepSeek(
        model= "deepseek-chat",
        api_key= os.environ.get("DEEPSEEK_API_KEY"),
    )

def DeepSeek_R1():
    return ChatDeepSeek(
        model= "deepseek-reasoner",
        api_key= os.environ.get("DEEPSEEK_API_KEY"),
    )

def Tongyi():
    return ChatOpenAI(
        model= "qwen-max",
        api_key= os.environ.get("TONGYI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        extra_body={
            # 开启深度思考，该参数对 QwQ 模型无效
            "enable_thinking": False
        },
    )