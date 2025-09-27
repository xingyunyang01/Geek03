import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent, BrowserProfile, Controller, BrowserSession
from browser_use.llm import ChatDeepSeek
from pydantic import BaseModel

class DYInfo(BaseModel):
    title: str
    video_url: str

# 创建一个更明确的Controller，添加系统提示
controller = Controller(
    output_model=DYInfo,
)

config = BrowserProfile(
    headless=True, #无头
    disable_security=True, #浏览器安全控制
    enable_default_extensions=False, #禁止下载扩展
    chromium_sandbox=False, #禁用沙盒
)

session = BrowserSession(browser_profile=config)

llm_deepseek = ChatDeepSeek(model= "deepseek-chat",
        api_key= os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1")

prompt = """你是一个抖音网页分析专家，擅长根据我的要求进行网页分析

只需在新标签页打开https://www.douyin.com/user/self?from_tab_name=main&modal_id=6750991424877071628&showTab=post，解析出网页标题及视频播放地址

无需任何解释或说明

若出现登录框请直接忽略，不影响视频解析"""

async def main():
    agent = Agent(
        task=prompt,
        llm=llm_deepseek,
        browser_session=session,
        controller=controller,
        use_vision=False,
    )
    ret=await agent.run()

    print(ret.final_result())

asyncio.run(main())