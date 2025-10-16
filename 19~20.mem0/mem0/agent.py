from langgraph.graph import StateGraph, START, END, MessagesState
from llm import Tongyi
from memconfig import m
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ChatState(MessagesState):
    mem0_user_id: str

llm = Tongyi()

def chat(state: ChatState):
    messages = state["messages"]
    user_id = state["mem0_user_id"]

    #召回记忆
    memories = m.search(messages[-1].content, user_id=user_id)

    context = "来自以往对话的相关信息：\n"
    for memory in memories.get('results', []):
        context += f"- {memory['memory']}\n"

    system_message = SystemMessage(content=f"""你是一个擅长解决客户问题的客服助手。请根据提供的上下文信息来个性化你的回答，并记住用户偏好和过往的交互。
{context}""")

    full_messages = [system_message] + messages
    response = llm.invoke(full_messages)

    state["messages"].append(response)

    return state

graph = StateGraph(ChatState)

graph.add_node("chat", chat)

graph.add_edge(START, "chat")
graph.add_edge("chat", END)

agent = graph.compile()

ret = agent.invoke({"mem0_user_id": "xyy", "messages": [HumanMessage(content="小明的爸爸喜欢喝什么饮料？")]})
print(ret)