import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  
    base_url="https://api.deepseek.com/v1"
)

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_closing_price",
            "description": "使用该工具获取指定股票的收盘价",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "股票名称",
                    }
                },
                "required": ["name"]
            },
        }
    },
]

def get_closing_price(name):
    if name == "青岛啤酒":
        return "67.92"
    elif name == "贵州茅台":
        return "1488.21"
    else:
        return "未搜到该股票"

if __name__ == "__main__":
    messages = [{"role": "user", "content": "青岛啤酒与贵州茅台的收盘价谁高？"}]
    while True:
        response = send_messages(messages)

        print("回复：")
        print(response.choices[0].message.content)

        print("工具选择：")
        print(response.choices[0].message.tool_calls)

        if response.choices[0].message.tool_calls != None:
            messages.append(response.choices[0].message)
            
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function.name == "get_closing_price":
                    arguments_dict = json.loads(tool_call.function.arguments)
                    price = get_closing_price(arguments_dict['name'])
                    
                    messages.append({
                        "role": "tool",
                        "content": price,
                        "tool_call_id": tool_call.id
                    })
        else:
            break
            