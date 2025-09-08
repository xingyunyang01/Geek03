import os
from openai import OpenAI
import json
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 初始化OpenAI客户端，配置阿里云DashScope服务
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("TONGYI_API_KEY"),  # 从环境变量读取API密钥
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 定义可用工具列表
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
    
messages = [{"role": "user", "content": "青岛啤酒与贵州茅台的收盘价谁高？"}]
while True:
    completion = client.chat.completions.create(
        model="qwen3-32b",
        messages=messages,
        extra_body={
            # 开启深度思考，该参数对 QwQ 模型无效
            "enable_thinking": True
        },
        tools=tools,
        parallel_tool_calls=True,
        stream=True,
        # 解除注释后，可以获取到token消耗信息
        # stream_options={
        #     "include_usage": True
        # }
    )

    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""     # 定义完整回复
    tool_info = []          # 存储工具调用信息
    is_answering = False   # 判断是否结束思考过程并开始回复
    print("="*20+"思考过程"+"="*20)
    for chunk in completion:
        if not chunk.choices:
            # 处理用量统计信息
            print("\n"+"="*20+"Usage"+"="*20)
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            # 处理AI的思考过程（链式推理）
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content
                print(delta.reasoning_content,end="",flush=True)  # 实时输出思考过程
                
            # 处理最终回复内容
            else:
                if not is_answering:  # 首次进入回复阶段时打印标题
                    is_answering = True
                    print("\n"+"="*20+"回复内容"+"="*20)
                if delta.content is not None:
                    answer_content += delta.content
                    print(delta.content,end="",flush=True)  # 流式输出回复内容
                
                # 处理工具调用信息（支持并行工具调用）
                if delta.tool_calls is not None:
                    for tool_call in delta.tool_calls:
                        index = tool_call.index  # 工具调用索引，用于并行调用
                        
                        # 动态扩展工具信息存储列表
                        while len(tool_info) <= index:
                            tool_info.append({})
                        
                        # 收集工具调用ID（用于后续函数调用）
                        if tool_call.id:
                            tool_info[index]['id'] = tool_info[index].get('id', '') + tool_call.id
                        
                        # 收集函数名称（用于后续路由到具体函数）
                        if tool_call.function and tool_call.function.name:
                            tool_info[index]['name'] = tool_info[index].get('name', '') + tool_call.function.name
                        
                        # 收集函数参数（JSON字符串格式，需要后续解析）
                        if tool_call.function and tool_call.function.arguments:
                            tool_info[index]['arguments'] = tool_info[index].get('arguments', '') + tool_call.function.arguments
    if not tool_info:
        break     
    else:
        # 将完整的模型回复添加到messages中
        messages.append({
            "content": answer_content,
            "refusal": None,
            "role": "assistant",
            "audio": None,
            "function_call": None,
            "tool_calls": [
                {
                    "id": tool['id'],
                    "function": {
                        "arguments": tool['arguments'],
                        "name": tool['name'],
                    },
                    "type": "function",
                    "index": idx,
                } for idx, tool in enumerate(tool_info)
            ],
        })
        # 处理所有收集到的工具调用
        for tool in tool_info:
            arguments_dict = json.loads(tool['arguments'])
            if tool['name'] == "get_closing_price":
                price = get_closing_price(arguments_dict['name'])
                messages.append({
                    "role": "tool",
                    "content": price,
                    "tool_call_id": tool['id']
                })
