from langchain_core.tools import tool

@tool
def add_tool(original_amount: int)-> int:
    """餐卡充值工具，入参为餐卡原始金额，出参为充值后的金额"""
    return original_amount+10