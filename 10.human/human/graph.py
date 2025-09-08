from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from llm import Tongyi
from typing_extensions import Literal
from tools import tools, tool_with_names
import sys
import io
import asyncio

llm_with_toools=Tongyi().bind_tools(tools)

class HumanState(MessagesState):
    query: str

async def run_graph():
    async def llm_node(state: HumanState):
        messages = [
            SystemMessage(content="你是一个仓库管理员,根据用户的要求回答相关的价格和库存信息"),
            HumanMessage(content=state["query"]),
        ] + state["messages"]

        response = await llm_with_toools.ainvoke(messages)

        state["messages"].append(response)

        return state

    async def human_node(state: HumanState):
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        # 终止 graph执行
        content = interrupt(state["messages"][-1].tool_calls[0]["args"])
        print("用户输入是:",content)
        
        tool_message = ToolMessage(
            tool_call_id=tool_call_id, 
            content=content
        )

        state["messages"].append(tool_message)

        return state

    async def tool_node(state: HumanState):
        ret = []
        for tool_call in state['messages'][-1].tool_calls:
            tool_name = tool_call['name']
            
            get_tool = tool_with_names[tool_name]
            print("调用工具：",tool_name,tool_call['args'])
            call_tool_ret= await get_tool.ainvoke(tool_call['args'])
                
            state["messages"].append(ToolMessage(content=call_tool_ret,
                                tool_call_id=tool_call['id']))

        return state

    def enter_tools(state):
        if state['messages'][-1].tool_calls:
            tool_call = state['messages'][-1].tool_calls[0]
            tool_name = tool_call['name']
            print("进入工具：",tool_name)
            print("参数为：",tool_call['args'])
            if tool_name=="ask_user":
                return "human_node"
            return "tool_node"
        return END

    graph = StateGraph(HumanState)

    graph.add_node("llm_node", llm_node)
    graph.add_node("human_node", human_node)
    graph.add_node("tool_node", tool_node)

    graph.add_edge(START, "llm_node")
    graph.add_conditional_edges("llm_node", enter_tools)
    graph.add_edge("tool_node", "llm_node")
    graph.add_edge("human_node", "llm_node")

    #Checkpoint保存在保留图状态的线程中，并且可以在图执行完成后访问。 这允许图执行在特定点暂停，等待人类批准，然后从最后一个checkpoint恢复执行
    memory = MemorySaver()
    graph = graph.compile(checkpointer=memory)

    thread_config = {"configurable": {"thread_id": "123"}}

    #第一次启动
    ret = await graph.ainvoke({"query": "我想买一些苹果，总共需要多少钱"},config=thread_config)

    if ret['messages'][-1].tool_calls and ret['messages'][-1].tool_calls[0]['name']=="ask_user":
        sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
        get_user_input=input("请输入用户输入：") 
        ret= await graph.ainvoke(Command( resume=get_user_input),config=thread_config)

    return ret['messages'][-1].content

if __name__ == "__main__":
    ret = asyncio.run(run_graph())
    print(ret)
