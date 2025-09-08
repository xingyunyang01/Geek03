import asyncio
import os
import yaml
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END,MessagesState
from prompts import SYSTEM_PROMPT
from llm import DeepSeek,Tongyi
from tools import get_closing_price
from typing_extensions import Literal
from typing import List, Dict
from pydantic import BaseModel, Field
from typing import List, Annotated, Tuple, Union, TypedDict
import operator

# 加载 .env 文件
load_dotenv()

class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

class Plan(BaseModel):  #实体对象
    """计划"""
    steps: List[str] = Field(
        description="要遵循的不同步骤应按顺序排列"
    )
    
class Response(BaseModel):
    """Response to user."""
    response: str


class Action(BaseModel):
    """执行的动作"""
    actions: Union[Response, Plan] = Field(
        description="要执行的动作,如果直接进行输出则选择Response,"
                    "如果需执行工具,请选择Plan"
    )

plan_prompt = ChatPromptTemplate.from_template(
    """ 
你是一个任务执行助手,根据给定的任务按步骤执行,不要添加任何多余的步骤 
最后一步的结果应该是最终答案。确保每个步骤都有所需的所有信息，不要跳过步骤

你的目标或问题:
{input}

你的计划是:
{plan}

当前已经完成的步骤:
{past_steps}

#请遵循以下规则
1.请输出JSON字符串,
2.相应地更新你的计划。如果不需要再执行更多步骤,就直接回复用户。否则，请填写计划。
3.只在计划中添加仍然需要完成的步骤。不要将之前完成的步骤作为计划的一部分返回。

#输出格式说明：
- 如果所有步骤都完成了，输出：{{"actions": {{"response": "最终回答内容"}}}}
- 如果还有步骤需要执行，输出：{{"actions": {{"steps": ["步骤1", "步骤2", ...]}}}}

注意：actions 字段是必需的，不要使用其他字段名。
""")
from langgraph.prebuilt import create_react_agent
class PlanAgent():
    def __init__(self,prompt_sys,plan=[],tools=[]):
        self.tools = tools
        llm=DeepSeek()
        llm2=Tongyi()
        self.plan=plan
        self.agent_executor = create_react_agent(llm, tools, prompt=prompt_sys )
        self.plan_executor = plan_prompt | \
                             llm2.with_structured_output(Action)

    async def execute_step(self,state: PlanExecute):
        plan = state["plan"]
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""计划有以下几个步骤:
{plan_str}\n\n你需要执行 步骤{1}. {task}."""
        print(task_formatted)
        agent_response = await self.agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        return {
            "past_steps": [(task, agent_response["messages"][-1].content)],
        }

    async def plan_step(self,state: PlanExecute):
        output = await self.plan_executor.ainvoke(state)
        if isinstance(output.actions, Response):
            return {"response": output.actions.response}
        else:
            return {"plan": output.actions.steps}

    def should_end(self,state: PlanExecute):
        if "response" in state and state["response"]:
            return END
        else:
            return "execute"

    async def run(self):
        workflow = StateGraph(PlanExecute)
        workflow.add_node("execute", self.execute_step)
        workflow.add_node("planstep", self.plan_step)

        workflow.add_edge(START, "execute")
        workflow.add_edge("execute", "planstep")

        workflow.add_conditional_edges(
            "planstep",
             self.should_end
        )
        app = workflow.compile()
        config = {"recursion_limit": 50}
        inputs = {"input": "完成所有计划后输出DONE",
                  "plan":self.plan}
        async for event in app.astream(inputs, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(v)


async def run_graph():
    plan=[
           "获取青岛啤酒的股票收盘价",
           "获取贵州茅台的股票收盘价",
           "比较青岛啤酒与贵州茅台的股票收盘价，得出哪个更贵的结论",
            ]
    tools=[get_closing_price]
    agent=PlanAgent(SYSTEM_PROMPT,plan,tools)
    await agent.run()

if __name__ == '__main__':

    asyncio.run(run_graph())