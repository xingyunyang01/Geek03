from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing_extensions import Literal
from webtools import widesearch_for_toolstr
from llm import Tongyi
from prompts import system_prompt
import asyncio

mcp_tools = {}
mcp_tools["common"] = {
    "url": "http://116.153.88.164:38001/mcp",
    "transport": "streamable_http",
}

llm = Tongyi()

class DeepThinkingAgent:
    async def run(self,question):
        mcp_client = MultiServerMCPClient(mcp_tools)
        tools = await mcp_client.get_tools()

        tools = tools + [widesearch_for_toolstr]

        tools_by_name = {tool.name: tool for tool in tools}

        llm_with_tools = llm.bind_tools(tools)

        async def llm_call(state: MessagesState):
            print("llm_call")
            messages = [
                SystemMessage(content=system_prompt),
            ] + state["messages"]

            response = await llm_with_tools.ainvoke(messages)

            state["messages"].append(response)

            return state

        async def tool_node(state):
            print("tool_node")
            for tool_call in state["messages"][-1].tool_calls:
                tool = tools_by_name[tool_call["name"]]
                observation = await tool.ainvoke(tool_call["args"])
                print("工具名称:",tool_call["name"])
                print("工具参数:",tool_call["args"])
                state["messages"].append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
            return state

        def should_continue(state) -> Literal["environment", "END"]:
            if state["messages"][-1].tool_calls:
                return "environment"
            return "END"

        agent_builder = StateGraph(MessagesState)

        agent_builder.add_node("llm_call", llm_call)
        agent_builder.add_node("environment", tool_node)

        agent_builder.add_edge(START, "llm_call")
        agent_builder.add_conditional_edges(
            "llm_call",
            should_continue,
            {
                # Name returned by should_continue : Name of next node to visit
                "environment": "environment",
                "END": END,
            },
        )
        agent_builder.add_edge("environment", "llm_call")

        agent = agent_builder.compile()

        messages = [HumanMessage(content=question)]
        ret = await agent.ainvoke({"messages": messages})

        return ret["messages"][-1].content
    
if __name__ == "__main__":
    agent = DeepThinkingAgent()
    result = asyncio.run(agent.run("请帮我总结一下DeepSeek-V3.1模型相关的股市热点新闻以及相关概念股，最后生成一份完整的MarkDown格式的分析报告"))
    print(result)