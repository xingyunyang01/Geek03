from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from .states import OverallState
from .llm import DeepSeek
from .tools.financial_indicator_A import get_financial_indicator_A
from .tools.financial_statements_A import get_balance_sheet_A, get_income_statement_A, get_cash_flow_statement_A
from .prompts import collect_financial_statement_prompt, collect_financial_indicator_prompt

class DataCollectionAgent():
    def run(self, stock_code: str, stock_name: str, market: str, year: str):
        def collect_financial_statement(state: OverallState):
            llm = DeepSeek()
            tools = [get_balance_sheet_A, get_income_statement_A, get_cash_flow_statement_A]

            formatted_prompt = collect_financial_statement_prompt.format(
                market=state["market"],
                stock_name=state["stock_name"],
                stock_code=state["stock_code"],
                year=state["year"],
            )

            print(formatted_prompt)
            
            sg=create_react_agent(llm, tools)

            ret = sg.invoke({"messages": [("user", formatted_prompt)]})

            print(ret)

            return state

        def collect_financial_indicator(state: OverallState):
            llm = DeepSeek()
            tools = [get_financial_indicator_A]
            
            formatted_prompt = collect_financial_indicator_prompt.format(
                market=state["market"],
                stock_name=state["stock_name"],
                stock_code=state["stock_code"],
                year=state["year"],
            )
            
            sg=create_react_agent(llm, tools)

            sg.invoke({"messages": [("user", formatted_prompt)]})

            return state
        
        builder = StateGraph(OverallState)

        builder.add_node("collect_financial_statement", collect_financial_statement)
        builder.add_node("collect_financial_indicator", collect_financial_indicator)

        builder.add_edge(START, "collect_financial_statement")
        builder.add_edge("collect_financial_statement", "collect_financial_indicator")
        builder.add_edge("collect_financial_indicator", END)

        graph = builder.compile()

        graph.invoke({"stock_code": stock_code, "stock_name": stock_name, "market": market, "year": year},{"recursion_limit": 60})