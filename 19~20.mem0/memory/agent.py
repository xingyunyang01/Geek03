from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import Literal
from llm import Tongyi
from tools import add_tool

llm = Tongyi()

tools = [add_tool]

tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = llm.bind_tools(tools)

def llm_call(state: MessagesState):
    #print("llm_call")
    messages = [
        SystemMessage(content="你是一个餐卡管理员，用户餐卡初始的金额为100元，请根据用户的问题进行餐卡的操作"),
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    state["messages"].append(response)

    return state

def tool_node(state):
    #print("tool_node")
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
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

memory=MemorySaver()
config = {"configurable": {"thread_id": "1"}}
agent = agent_builder.compile(checkpointer=memory)

messages = [HumanMessage(content="请帮我充值10元，并告诉我充值后的餐卡余额")]
ret = agent.invoke({"messages": messages}, config=config)

print(ret["messages"][-1].content)

messages = [HumanMessage(content="请帮我充值10元，并告诉我充值后的餐卡余额")]
ret = agent.invoke({"messages": messages}, config=config)

print(ret["messages"][-1].content)
