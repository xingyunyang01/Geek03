import os
import asyncio
import datetime

from dotenv import load_dotenv
from smolagents import CodeAgent
from llm import codeModel,toolModel,zhipuModel
from subagent import get_search_agent_stock
#from tools import find_csv

load_dotenv()

system_prompt="""
你是一个专业的量化交易分析师，请根据用户需求对股票日K线DataFrame进行操作。DataFrame结构如下：
**列名说明:**
- 日期 (datetime格式)
- 股票代码 (string)
- 开盘, 收盘, 最高, 最低 (float)
- 成交量 (int), 成交额 (float)
- 振幅, 涨跌幅, 涨跌额, 换手率 (float)

**代码规则:**
1. 使用pandas库读取csv文件,文件路径是:{csv_path}
参考代码:df = pd.read_csv(csvfile_path,dtype={{'股票代码': str}})
2. 强制日期转换：`df['日期'] = pd.to_datetime(df['日期'])`
3. 仅使用Pandas进行向量化操作
4. 处理多股票时自动分组
5. **绝对禁止任何绘图操作**（Matplotlib/mplfinance等）
6. 当前日期是: {current_date}
7. 代码应该做好非空判断或索引有效性判断
 


用户问题:
{user_question}
"""

async def main(user_question:str):
    #csvfile = find_csv()
    csvfile = "/root/python/smolagents/files/data/600600.csv"
    filled_system_prompt= system_prompt.format(csv_path=csvfile,
                                               user_question=user_question,
                                                current_date=datetime.datetime.now().strftime("%Y-%m-%d"))
    agent = CodeAgent(
        model=toolModel,
        tools=[],
        max_steps=20,
        verbosity_level=2,
        additional_authorized_imports=["pandas", "numpy", "datetime"],
        planning_interval=3,
        managed_agents=[get_search_agent_stock(toolModel)],
        stream_outputs=True
    )

    agent.run(filled_system_prompt)

if __name__ == '__main__':
    asyncio.run(main("分析青岛啤酒2024年9月份是否存在跳空高开的情况"))