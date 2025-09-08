from langchain_core.messages import AIMessage, SystemMessage,HumanMessage, ToolMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph import START, END
from langgraph.graph.message import add_messages
from llm import Tongyi
from prompts import SYSTEM_PROMPT
from typing import Annotated, TypedDict
from tools import tools

llm_Tongyi = Tongyi()

class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    actions: list[dict]
    output: str
    user_prompt: str

class CodeActGraph():
    def run(self, user_prompt: str):
        def _create_agent_action(ai_message):
            # 提取代码部分
            content = ai_message.content
            if "```python" in content:
                code_blocks = content.split("```python")
                code = code_blocks[1].split("```")[0].strip()
                return {"tool": "execute_python", "tool_input": code}
            return None

        def llm_call(state: OverallState):
            # 构建包含系统提示词和用户提示词的消息列表
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=state["user_prompt"])
            ]+state["messages"]

            ret = llm_Tongyi.invoke(messages)

            action = _create_agent_action(ret)
            if action:
                return {"messages": [ret], "actions": [action], "output": ""}
            return {"messages": [ret], "output": ret.content}

        def enter_process(state: OverallState):
            if state["output"] != "":
                return END
            return "process_node"

        def process_node(state: OverallState):
            actions = state["actions"]
            for action in actions:
                tool_name = action["tool"]
                tool_input = action["tool_input"]
                tool_fn = next(t for t in tools if t.name == tool_name)
                observation = tool_fn.invoke(tool_input)  #执行工具
                state["messages"].append(HumanMessage(content=f"##执行结果:\n{observation}"))

            return state

        graph = StateGraph(OverallState)
        graph.add_node("llm_call", llm_call)
        graph.add_node("enter_process", enter_process)
        graph.add_node("process_node", process_node)

        graph.add_edge(START, "llm_call")
        graph.add_conditional_edges("llm_call",enter_process)
        graph.add_edge("process_node", "llm_call")

        agent = graph.compile()
        ret = agent.invoke(OverallState(user_prompt=user_prompt))
        
        return ret["output"]

if __name__ == "__main__":
    graph = CodeActGraph()
    ret = graph.run("请计算1~100的和")
    print(ret)
