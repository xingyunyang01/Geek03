import os

from .tools_and_schemas import SearchQueryList, Reflection, widesearch_for_toolstr
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from .state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from .configuration import Configuration
from .prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from langchain_deepseek import ChatDeepSeek
from .utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

load_dotenv()

if os.getenv("TONGYI_API_KEY") is None:
    raise ValueError("TONGYI_API_KEY is not set")

if os.getenv("DEEPSEEK_API_KEY") is None:
    raise ValueError("DEEPSEEK_API_KEY is not set")

def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """基于用户问题生成搜索查询的LangGraph节点。

    使用deepseek-chat模型为用户问题创建优化的网络研究搜索查询。

    参数:
        state: 包含用户问题的当前图状态
        config: 可运行配置，包括LLM提供商设置

    返回:
        包含状态更新的字典，包括search_query键，其中包含生成的查询
    """

    configurable = Configuration.from_runnable_config(config)

    # 检查是否自定义初始搜索查询数量
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # init deepseek-chat
    llm = ChatDeepSeek(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    return {"search_query": result.query}

def continue_to_web_research(state: QueryGenerationState):
    """发送搜索请求给web_research节点.

    用于生成n个web_research节点，每个节点对应一个搜索查询。
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]

def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """使用Searx搜索API工具执行web research的LangGraph节点.

    使用博查搜索API工具执行网络研究。

    参数:
        state: 包含搜索查询和研究循环计数的当前图状态
        config: 可运行配置，包括搜索API设置

    返回:
        包含状态更新的字典，包括research_loop_count和web_research_results
    """
    # Configure
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    # Uses the google genai client as the langchain client doesn't return grounding metadata
    llm = ChatDeepSeek(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    tools = [widesearch_for_toolstr]
    agent = create_react_agent(
        llm,
        tools,
    )

    response = agent.invoke({"messages": [("user", formatted_prompt)]})
    
    # 取出response中最后一条message的content
    last_message_content = ""
    if response["messages"]:
        last_message = response["messages"][-1]
        last_message_content = last_message.content
    
    #print("Last message content:", last_message_content)

    return {
        "search_query": [state["search_query"]],
        "web_research_result": [last_message_content],
    }

def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """识别知识差距并生成潜在后续查询的 LangGraph 节点.

    分析当前摘要以确定需要进一步研究的领域，并生成可能的后续查询。使用结构化输出进行提取JSON 格式的后续查询。

    Args:
        state: 当前图状态，包含正在运行的摘要和研究主题
        config: 可运行配置，包括LLM提供商设置

    Returns:
        包含状态更新的字典，包括search_query键，其中包含生成的后续查询
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model", configurable.reflection_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # init Reasoning Model
    llm = ChatDeepSeek(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    print(result)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }

def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph 路由功能，用于确定研究流程的下一步.

    通过决定是否继续收集信息来控制研究循环或者根据配置的最大研究循环数完成摘要。

    Args:
        state: 当前图状态，包含研究循环计数
        config: 可运行配置，包括max_research_loops设置

    Returns:
        指示下一个要访问的节点（"web_research" 或 "finalize_summary"）的字符串文字
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]

def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph 节点，用于完成研究摘要。

    通过对资料来源进行复制和格式化，准备最终成果，然后将其与流水账式摘要相结合，创建结构合理的研究报告，并适当引用。

    Args:
        state: 当前图状态，包含正在运行的摘要和收集的来源

    Returns:
        包含状态更新的字典，包括running_summary键，其中包含格式化的最终摘要和来源
    """
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # init Reasoning Model, default to Gemini 2.5 Flash
    llm = ChatDeepSeek(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    result = llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=result.content)],
    }

builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("evaluate_research", evaluate_research)
builder.add_node("finalize_answer", finalize_answer)

builder.add_edge(START, "generate_query")
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
builder.add_edge("web_research", "reflection")
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")

if __name__ == "__main__":
    ret=graph.invoke({"messages": [HumanMessage(content="请从行业内主要上市公司中找出与商汤科技市值规模与业务规模相似，业务重叠度高的公司")]})
    last_message_content = ""
    if ret["messages"]:
        last_message = ret["messages"][-1]
        last_message_content = last_message.content
    print(last_message_content)