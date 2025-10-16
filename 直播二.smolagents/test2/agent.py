import os
import asyncio

from dotenv import load_dotenv
from smolagents import CodeAgent
from llm import codeModel,toolModel,zhipuModel
from tools import GetKlineData,GetCjNews
from subagent import get_search_agent_stock

load_dotenv()

async def main():
    tools = [GetKlineData(),GetCjNews()]
    agent = CodeAgent(
        model=toolModel,
        tools=tools,
        max_steps=20,
        verbosity_level=2,
        additional_authorized_imports=["*"],
        planning_interval=4,
        managed_agents=[get_search_agent_stock(toolModel)],
        stream_outputs=True
    )

    agent.run("""
你是一个股票分析助手.获取最新的财经新闻，并分析总结，不超过500字,输出必须使用中文
""")

if __name__ == '__main__':
    asyncio.run(main())