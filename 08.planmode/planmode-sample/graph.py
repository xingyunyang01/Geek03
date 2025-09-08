from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from llm import Tongyi
from prompts import PLAN_PROMPT, PLAN_EXECUTE_PROMPT
from typing_extensions import Literal
from tools import tools, tools_by_name

llm_Tongyi = Tongyi()
llm_with_tools = llm_Tongyi.bind_tools(tools)

class PlanState(MessagesState):
    plan: str

def plan_node(state: PlanState):
    # 调用 LLM
    response = llm_Tongyi.invoke([SystemMessage(content=PLAN_PROMPT),state["messages"][0]])
    
    state["plan"] = response.content
    print("计划：\n" + state["plan"])
    return state

def execute_node(state: PlanState):
    messages = [
        SystemMessage(
            content=PLAN_EXECUTE_PROMPT.format(plan=state["plan"])
        )
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)
    state["messages"].append(response)
    
    return state

def tool_node(state: PlanState):
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        state["messages"].append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return state

def should_continue(state: PlanState) -> Literal["tool_node", "END"]:
    messages = state["messages"]
    last_message = messages[-1]
    if "Final Answer" in last_message.content:
        return "END"
    return "tool_node"

agent_builder = StateGraph(PlanState)

# Add nodes
agent_builder.add_node("plan_node", plan_node)
agent_builder.add_node("execute_node", execute_node)
agent_builder.add_node("tool_node", tool_node)

# Add edges
agent_builder.add_edge(START, "plan_node")
agent_builder.add_edge("plan_node", "execute_node")
agent_builder.add_conditional_edges(
    "execute_node",
    should_continue,
    {
        "tool_node": "tool_node",
        "END": END,
    },
)
agent_builder.add_edge("tool_node", "execute_node")

agent = agent_builder.compile()

ret = agent.invoke({"plan":"", "messages": [HumanMessage(content="茅台和青岛啤酒哪个贵？")]})
print(ret["messages"][-1].content)