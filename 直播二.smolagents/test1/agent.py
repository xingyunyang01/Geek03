import os
from dotenv import load_dotenv
from smolagents import OpenAIServerModel, CodeAgent, WebSearchTool
from tools import BoChaSearchTool
from llm import zhipuModel,codeModel,toolModel

agent = CodeAgent(tools=[BoChaSearchTool()], model=toolModel, stream_outputs=True)

agent.run("优必选近期有什么利好消息？")