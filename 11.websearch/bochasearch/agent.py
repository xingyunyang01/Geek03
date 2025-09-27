from tools import bocha_for_detail
from llm import client
import asyncio

SYSTEM_PROMPT="""
你是一个股票专家，请根据上下文回答用户的问题。

#上下文：
{context}

# 用户的问题是：
{query}
"""

async def run(query:str):
    ret=await bocha_for_detail(query)
    print(ret)

    prompt = SYSTEM_PROMPT.format(context=ret,query=query)

    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content
    
if __name__ == "__main__":
    ret=asyncio.run(run("商汤科技是在哪上市的？"))
    print(ret)