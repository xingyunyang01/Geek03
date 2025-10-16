from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from .llm import DeepSeek, DeepSeek_R1, Tongyi
from .prompts import analyze_system_prompt, analyze_user_prompt
from .tools.financial_caculate import calculate_quick_ratio, calculate_total_asset_turnover, calculate_receivables_turnover_days, calculate_inventory_turnover_days, calculate_cash_flow_matching_ratio, calculate_sales_cash_ratio, calculate_equity_multiplier, calculate_gross_profit_margin, calculate_net_profit_margin, calculate_debt_to_asset_ratio, calculate_current_ratio
from .states import OverallState
from .utils import get_financial_statements_file_map, read_csv, save_dataframe_to_csv_file  

class FinancialCaculateAgent():
    def run(self, stock_code: str, stock_name: str, market: str, year: str):
        def analyze_financial_data(state: OverallState):
            file_map = get_financial_statements_file_map()
            files = []
            stock_code = state["stock_code"]
            year = state["year"]
            if stock_code in file_map:
                year_map = file_map[stock_code]
                if year in year_map:
                    files = year_map[year]
            
            report0=read_csv(files[0])
            report1=read_csv(files[1])
            report2=read_csv(files[2])
            report3=read_csv(files[3])

            llm = Tongyi()
            tools = [calculate_quick_ratio, 
                     calculate_total_asset_turnover, 
                     calculate_receivables_turnover_days, 
                     calculate_inventory_turnover_days, 
                     calculate_cash_flow_matching_ratio, 
                     calculate_sales_cash_ratio, 
                     calculate_equity_multiplier,
                     calculate_gross_profit_margin,
                     calculate_net_profit_margin,
                     calculate_debt_to_asset_ratio,
                     calculate_current_ratio]
            
            formatted_system_prompt = analyze_system_prompt.format(company_name=state["stock_name"], year=state["year"])
            formatted_user_prompt = analyze_user_prompt.format(company_name=state["stock_name"], year=state["year"], files0=files[0], report0=report0, files1=files[1], report1=report1, files2=files[2], report2=report2, files3=files[3], report3=report3)

            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=formatted_system_prompt
            )

            agent_response = agent.invoke({"messages": formatted_user_prompt})

            # INSERT_YOUR_CODE
            import pandas as pd
            import json
            # 解析JSON字符串为字典
            result_json = agent_response["messages"][-1].content
            try:
                result_dict = json.loads(result_json)
            except Exception:
                # 若content前后有多余内容，尝试提取大括号内的JSON
                import re
                match = re.search(r"\{[\s\S]*\}", result_json)
                if match:
                    result_dict = json.loads(match.group(0))
                else:
                    raise ValueError("无法解析agent返回的JSON内容")
            # 转为DataFrame
            df = pd.DataFrame([result_dict])
            # 写入csv文件
            save_dataframe_to_csv_file(df, f"{stock_code}_{year}年度财务计算结果.csv")

            return {"messages": agent_response["messages"][-1].content}
        
        builder = StateGraph(OverallState)

        builder.add_node("analyze_financial_data", analyze_financial_data)

        builder.add_edge(START, "analyze_financial_data")
        builder.add_edge("analyze_financial_data", END)

        graph = builder.compile()

        ret = graph.invoke({"stock_code": stock_code, "stock_name": stock_name, "market": market, "year": year},{"recursion_limit": 60})
        
        return ret["messages"][-1].content
    
if __name__ == "__main__":
    agent = FinancialCaculateAgent()
    ret=agent.run("00020", "商汤科技", "港股", "2024")
    print(ret)
        
