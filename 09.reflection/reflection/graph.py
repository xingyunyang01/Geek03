from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from llm import Tongyi
from prompts import COMMAND_PROMPT, REFLECTION_PROMPT
from typing_extensions import Literal
from typing import TypedDict

stop_sign=["安全隐患","木马","攻击"]
class AgentState(TypedDict):
    user_query: str #用户提问
    best_command: str #当前最优方案
    reflection: str #反思记录
    iterations: int  #执行次数

llm_Tongyi=Tongyi()

def generate_command(state: AgentState):
    iter=state["iterations"]
    print(f"生成第{iter+1}次命令")
    if iter==0: # 第一次生成
        prompt = COMMAND_PROMPT.format(
            user_query=state["user_query"],
            best_command="无",
            reflection="无"
        )
    else:
        prompt = REFLECTION_PROMPT.format(
            user_query=state["user_query"],
            best_command=state["best_command"],
            reflection=state["reflection"]
        )
 
    response = llm_Tongyi.invoke(prompt)
    content = response.content
    command = content.split("命令：")[1].strip()
    iterations = state["iterations"] + 1
    return {"best_command": command,"iterations":iterations}

def reflect_and_optimize(state: AgentState):
    print("执行反思检查")

    prompt=REFLECTION_PROMPT.format(
        command=state["best_command"],
        user_query=state["user_query"]
    )
    response = llm_Tongyi.invoke(prompt)
    content = response.content
    if "无建议" in content  or  "无需优化" in content:
        return {"reflection": "已经最优,无需优化", }
    reflection=content.split("检查结果：")[1].strip()
    return {"reflection": reflection, }

def check_reflection(state):
    if "无建议" in state["reflection"]  or  "无需优化" in state["reflection"]:
        print("已经最优,无需优化")
        return END
    for stop in stop_sign:
        if stop in state["reflection"]:
            print("检测到停止标志，结束")
            return END
    if state["iterations"] >= 3:  # 最多三次迭代就结束
        print("迭代次数已达上限，结束")
        return END

    return "generate"

workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("generate", generate_command)
workflow.add_node("reflect", reflect_and_optimize)

# 设置边
workflow.set_entry_point("generate")
workflow.add_edge("generate", "reflect")

workflow.add_conditional_edges(  #条件
    "reflect",
    check_reflection
)

graph = workflow.compile()

ret = graph.invoke({"user_query": "使用docker创建nginx容器,端口映射8080:80",
        "best_command": "",
        "reflection":"",
        "iterations":0})

print("命令结果:",ret["best_command"])
print("反思结果:",ret["reflection"])