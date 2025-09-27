from tools import tools
from llm import Tongyi
from langgraph.prebuilt import create_react_agent
import asyncio
from prompts import SYSTEM_PROMPT,SYSTEM_PROMPT2

async def run(query:str):
    llm=Tongyi()
    agent=create_react_agent(llm,tools)
    prompt=SYSTEM_PROMPT2.format(query=query)
    response=await agent.ainvoke({"messages": [("user", prompt)]})
    
    return response["messages"][-1].content
    
if __name__ == "__main__":
    ret=asyncio.run(run("商汤科技是在哪个交易所上市的？最新的股价是多少，最近有什么相关新闻利好消息？请对以上回答内容进行总结后，生成一份报告"))
    print(ret)