from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langgraph.prebuilt import create_react_agent
from .tools.stock_info_A import get_stock_intro
from .llm import DeepSeek
from .prompts import collect_stock_info_prompt
from typing_extensions import Literal

class StockInfoCollectionAgent():
    def run(self, stock_code: str, stock_name: str, market: str):
        llm = DeepSeek()
        tools = [get_stock_intro]
        
        formatted_prompt = collect_stock_info_prompt.format(
            stock_code=stock_code,
            stock_name=stock_name,
            market=market,
        )
        
        sg=create_react_agent(llm, tools)

        ret = sg.invoke({"messages": [("user", formatted_prompt)]})
        return ret["messages"][-1].content





