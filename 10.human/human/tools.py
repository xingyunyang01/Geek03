from langchain_core.tools import tool
import random

@tool
async def get_stock(product):
    """获取商品库存"""
    stock = random.randint(0, 100)
    return f"商品{product}的库存为{stock}件"

@tool
async def get_price(product):
    """获取商品价格"""
    price = random.uniform(10, 100)
    return f"商品{product}的价格为{price:.2f}元"

@tool
async def ask_user(ask_user_question):
    """询问用户进一步的需求，如用户要多少件商品、要什么商品等"""
    print(ask_user_question)
    pass

tools=[get_stock,get_price,ask_user]
tool_with_names={tool.name: tool for tool in tools}