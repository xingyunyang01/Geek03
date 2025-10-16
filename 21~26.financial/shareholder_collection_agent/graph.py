from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from .tools.shareholder_structure_A import ak_stock_gdfx_top_10, ak_stock_gdfx_free_top_10, ak_stock_main_stock_holder, ak_stock_restricted_release_queue_sina
from .llm import DeepSeek
from .prompts import collect_shareholder_structure_prompt
from typing_extensions import Literal

class ShareholderCollectionAgent():
    def run(self, stock_code: str, stock_name: str, market: str):
        llm = DeepSeek()
        tools = [ak_stock_gdfx_top_10, ak_stock_gdfx_free_top_10, ak_stock_main_stock_holder, ak_stock_restricted_release_queue_sina]
        
        formatted_prompt = collect_shareholder_structure_prompt.format(
            market=market,
            stock_name=stock_name,
            stock_code=stock_code,
        )
        
        sg=create_react_agent(llm, tools)

        ret = sg.invoke({"messages": [("user", formatted_prompt)]})
        return ret["messages"][-1].content





