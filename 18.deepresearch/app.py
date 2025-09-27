import streamlit as st
import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from agent.graph import graph
from agent.configuration import Configuration
import time

# 页面配置
st.set_page_config(
    page_title="深度研究助手",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "config" not in st.session_state:
    st.session_state.config = Configuration()

if "execution_steps" not in st.session_state:
    st.session_state.execution_steps = []

def reset_conversation():
    """重置对话历史"""
    st.session_state.messages = []
    st.session_state.execution_steps = []

def update_config():
    """更新配置"""
    try:
        st.session_state.config = Configuration(
            query_generator_model=st.session_state.query_generator_model,
            reflection_model=st.session_state.reflection_model,
            answer_model=st.session_state.answer_model,
            number_of_initial_queries=st.session_state.number_of_initial_queries,
            max_research_loops=st.session_state.max_research_loops
        )
        st.success("配置已更新！")
    except Exception as e:
        st.error(f"配置更新失败: {str(e)}")

def stream_graph_execution(user_input: str):
    """流式执行graph并收集执行步骤"""
    st.session_state.execution_steps = []
    
    # 准备配置
    config = {
        "configurable": {
            "query_generator_model": st.session_state.config.query_generator_model,
            "reflection_model": st.session_state.config.reflection_model,
            "answer_model": st.session_state.config.answer_model,
            "number_of_initial_queries": st.session_state.config.number_of_initial_queries,
            "max_research_loops": st.session_state.config.max_research_loops
        }
    }
    
    try:
        # 流式执行
        for event in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        ):
            for node_name, node_output in event.items():
                if node_name != "__end__":
                    step_info = {
                        "node": node_name,
                        "output": node_output,
                        "timestamp": time.time()
                    }
                    st.session_state.execution_steps.append(step_info)
                    yield step_info
    except Exception as e:
        # 记录错误信息
        error_step = {
            "node": "error",
            "output": {"error": str(e)},
            "timestamp": time.time()
        }
        st.session_state.execution_steps.append(error_step)
        yield error_step

def render_execution_step(step: Dict[str, Any]):
    """渲染单个执行步骤"""
    # 根据节点类型选择不同的图标
    node_icons = {
        "generate_query": "🔍",
        "web_research": "🌐", 
        "reflection": "🤔",
        "evaluate_research": "⚖️",
        "finalize_answer": "📝",
        "error": "❌"
    }
    
    icon = node_icons.get(step['node'], "🔧")
    
    with st.expander(f"{icon} {step['node']}", expanded=True):
        st.write(f"**执行时间:** {time.strftime('%H:%M:%S', time.localtime(step['timestamp']))}")
        
        # 处理错误情况
        if step['node'] == 'error':
            st.error(f"执行出错: {step['output'].get('error', '未知错误')}")
            return
        
        if isinstance(step['output'], dict):
            for key, value in step['output'].items():
                if key == "search_query" and isinstance(value, list):
                    st.write(f"**{key}:**")
                    for i, query in enumerate(value, 1):
                        st.code(f"{i}. {query}")
                elif key == "web_research_result" and isinstance(value, list):
                    st.write(f"**{key}:**")
                    for i, result in enumerate(value, 1):
                        with st.expander(f"搜索结果 {i}"):
                            st.markdown(result)
                elif key == "messages" and isinstance(value, list):
                    st.write(f"**{key}:**")
                    for msg in value:
                        if hasattr(msg, 'content'):
                            st.markdown(msg.content)
                elif key == "is_sufficient":
                    st.write(f"**{key}:** {'✅ 信息充足' if value else '❌ 需要更多信息'}")
                elif key == "knowledge_gap":
                    st.write(f"**{key}:**")
                    st.info(value)
                elif key == "follow_up_queries" and isinstance(value, list):
                    st.write(f"**{key}:**")
                    for i, query in enumerate(value, 1):
                        st.code(f"{i}. {query}")
                else:
                    st.write(f"**{key}:**")
                    if isinstance(value, str) and len(value) > 200:
                        with st.expander("查看详细内容"):
                            st.markdown(value)
                    else:
                        st.write(value)
        else:
            st.write(step['output'])

# 侧边栏 - 配置面板
with st.sidebar:
    st.title("⚙️ 配置设置")
    
    # 配置预设
    st.subheader("🚀 快速预设")
    preset = st.selectbox(
        "选择配置模式",
        ["自定义", "快速模式", "标准模式", "深度模式"],
        help="快速模式：1个查询，1轮循环（适合简单问题）\n标准模式：3个查询，2轮循环（平衡性能和效果）\n深度模式：5个查询，3轮循环（适合复杂研究）"
    )
    
    if preset == "快速模式":
        st.session_state.query_generator_model = "deepseek-chat"
        st.session_state.reflection_model = "deepseek-chat"
        st.session_state.answer_model = "deepseek-chat"
        st.session_state.number_of_initial_queries = 1
        st.session_state.max_research_loops = 1
    elif preset == "标准模式":
        st.session_state.query_generator_model = "deepseek-chat"
        st.session_state.reflection_model = "deepseek-chat"
        st.session_state.answer_model = "deepseek-chat"
        st.session_state.number_of_initial_queries = 3
        st.session_state.max_research_loops = 2
    elif preset == "深度模式":
        st.session_state.query_generator_model = "deepseek-chat"
        st.session_state.reflection_model = "deepseek-chat"
        st.session_state.answer_model = "deepseek-chat"
        st.session_state.number_of_initial_queries = 5
        st.session_state.max_research_loops = 3
    
    # 模型配置
    st.subheader("🤖 模型配置")
    st.text_input(
        "查询生成模型",
        value=st.session_state.config.query_generator_model,
        key="query_generator_model",
        help="用于生成搜索查询的LLM模型名称"
    )
    st.text_input(
        "反思模型",
        value=st.session_state.config.reflection_model,
        key="reflection_model",
        help="用于反思和信息评估的LLM模型名称"
    )
    st.text_input(
        "回答模型",
        value=st.session_state.config.answer_model,
        key="answer_model",
        help="用于生成最终答案的LLM模型名称"
    )
    
    # 参数配置
    st.subheader("📊 参数配置")
    st.number_input(
        "初始查询数量",
        min_value=1,
        max_value=10,
        value=st.session_state.config.number_of_initial_queries,
        key="number_of_initial_queries",
        help="设置初始搜索查询的数量"
    )
    st.number_input(
        "最大研究循环",
        min_value=1,
        max_value=5,
        value=st.session_state.config.max_research_loops,
        key="max_research_loops",
        help="设置最大研究循环次数"
    )
    
    # 配置按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 更新配置", on_click=update_config):
            pass
    with col2:
        if st.button("🔄 重置对话", on_click=reset_conversation):
            pass
    
    # 显示当前配置
    st.subheader("📋 当前配置")
    with st.expander("查看详细配置"):
        st.json(st.session_state.config.model_dump())

# 主界面
st.title("🔍 深度研究助手")
st.markdown("基于LangGraph的智能研究助手，支持多轮搜索和深度分析")

# 对话界面
st.subheader("💬 对话")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的研究问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 创建助手消息占位符
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 执行步骤显示区域
        execution_container = st.container()
        
        # 流式执行
        step_count = 0
        total_steps = 5  # 预估总步骤数
        
        for step in stream_graph_execution(prompt):
            step_count += 1
            progress = min(step_count / total_steps, 1.0)
            progress_bar.progress(progress)
            
            # 更新状态文本
            status_text.text(f"正在执行: {step['node']}...")
            
            # 更新执行步骤显示
            with execution_container:
                render_execution_step(step)
            
            # 检查是否有最终回答
            if step['node'] == 'finalize_answer' and 'messages' in step['output']:
                for msg in step['output']['messages']:
                    if hasattr(msg, 'content'):
                        full_response = msg.content
                        message_placeholder.markdown(full_response)
            
            # 检查是否有错误
            if step['node'] == 'error':
                full_response = f"执行过程中出现错误: {step['output'].get('error', '未知错误')}"
                message_placeholder.error(full_response)
                break
        
        # 完成进度条
        progress_bar.progress(1.0)
        status_text.text("执行完成！")
        
        # 如果没有找到最终回答，显示执行完成
        if not full_response:
            full_response = "研究完成，请查看执行步骤了解详细过程。"
            message_placeholder.markdown(full_response)
    
    # 添加助手消息到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 执行步骤历史
if st.session_state.execution_steps:
    st.subheader("📋 执行步骤历史")
    for step in st.session_state.execution_steps:
        render_execution_step(step)

# 页脚
st.markdown("---")
st.markdown("💡 **提示:** 您可以在侧边栏调整配置参数来优化研究效果") 