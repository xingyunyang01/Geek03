import datetime
from smolagents import ToolCallingAgent
from tools import BochaSearchTool

def get_search_agent_stock(model):
    description = """
你是一个股票搜索助手,根据用户问题进行关键字搜索.并遵循以下规则:
1. 拆分复杂问题：将用户的多维度查询分解为2-3个核心子主题
2. 渐进式搜索：每次只搜索1-3个高度相关的关键词组合
3. 迭代优化：基于首次搜索结果，动态调整后续关键词
4. 关键词纪律：单次搜索关键词不超过3个，禁止罗列所有关键词
当前日期是:{current_date},你应该搜索近3天的新闻     
"""
    description=description.format(current_date=datetime.datetime.now().strftime("%Y-%m-%d"))
    tools = [BochaSearchTool()]
    # Initialize the search tool to be used by the agent
    search_agent = ToolCallingAgent(
    # Create and configure the ToolCallingAgent with specified parameters
        model=model,
        tools=tools,                    # The model for processing queries
        max_steps=20,                    # Available tools for the agent
        verbosity_level=2,                   # Maximum steps the agent can take
        planning_interval=4,              # Level of detail in output
        name="search_agent",            # Interval for planning steps
        description=description,            # Name identifier for the agent
        provide_run_summary=True,
    )
    return  search_agent