import os
from dotenv import load_dotenv
from smolagents import OpenAIServerModel

load_dotenv()

codeModel = OpenAIServerModel(
    model_id="qwen3-coder-plus",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1", # Leave this blank to query OpenAI servers.
    api_key=os.environ["TONGYI_API_KEY"], # Switch to the API key for the server you're targeting.
)

zhipuModel = OpenAIServerModel(
    model_id="glm-4.5",
    api_base="https://open.bigmodel.cn/api/paas/v4", # Leave this blank to query OpenAI servers.
    api_key=os.environ["ZHIPU_API_KEY"], # Switch to the API key for the server you're targeting.
    extra_body={
        "thinking": {
            "type": "disabled",
        },
    }
)

toolModel = OpenAIServerModel(
    model_id="qwen-max",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1", # Leave this blank to query OpenAI servers.
    api_key=os.environ["TONGYI_API_KEY"], # Switch to the API key for the server you're targeting.
)