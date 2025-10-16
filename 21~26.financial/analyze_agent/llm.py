import os
import yaml
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
        model= "qwen3-coder-plus",
        api_key= os.environ.get("TONGYI_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        extra_body={
            # 开启深度思考，该参数对 QwQ 模型无效
            "enable_thinking": False
        },
    )

def parse_yaml_response(response: str) -> dict:
        """解析YAML格式的响应"""
        try:
            # 提取```yaml和```之间的内容
            if '```yaml' in response:
                start = response.find('```yaml') + 7
                end = response.find('```', start)
                yaml_content = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                yaml_content = response[start:end].strip()
            else:
                yaml_content = response.strip()
            
            return yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"YAML解析失败: {e}")
            print(f"原始响应: {response}")
            return {}