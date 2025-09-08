from langchain.agents import tool

@tool
def get_closing_price(name: str) -> str:
    """获取股票的收盘价"""
    if name == "青岛啤酒":
        return "67.92"
    elif name == "贵州茅台":
        return "1488.21"
    else:
        return "未搜到该股票"

tools = [get_closing_price]
tools_by_name = {tool.name: tool for tool in tools}