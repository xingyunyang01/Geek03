tools = [
    {
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
    },
]

def get_closing_price(name):
    if name == "青岛啤酒":
        return "67.92"
    elif name == "贵州茅台":
        return "1488.21"
    else:
        return "未搜到该股票"