import akshare as ak
import pandas as pd
from typing import Dict, Optional
from langchain_core.tools import tool
import os

def financial_indicator_A(stock_code: str = "600600", start_year: str = "2024") -> pd.DataFrame:
    """
    获取A股公司的财务指标
    
    Args:
        stock_code (str): 股票代码
        start_year (str): 开始查询的年份时间，比如2024
    
    Returns:
        pd.DataFrame: 资产负债表数据，如果获取失败则返回None
    """
    try:
        df_financial_sheet = ak.stock_financial_analysis_indicator(symbol=stock_code,start_year=start_year)
        # 只获取日期为2024-12-31的数据
        # 筛选出日期为2024-12-31的数据行
        # 检查数据中是否有2024-12-31的数据，如果没有则获取最新的数据
        # 将日期转换为字符串进行比较，因为日期列是datetime.date类型
        if f'{start_year}-12-31' in df_financial_sheet['日期'].astype(str).values:
            print(f"有{start_year}-12-31的数据")
            df_financial_sheet = df_financial_sheet[df_financial_sheet['日期'].astype(str) == f'{start_year}-12-31']
        
        return df_financial_sheet
    
    except Exception as e:
        print(f"获取财务指标失败: {e}")
        return None
    
@tool
def get_financial_indicator_A(symbol: str = "600600", start_year: str = "2024"):
    """
    获取A股公司的财务指标，并保存到文件中
    
    Args:
        symbol (str): 股票代码，如：600600
        start_year (str): 开始查询的年份时间，比如2024
    
    Returns:
        path (str): 保存A股财务指标文件的路径
    """
    financial_indicator=financial_indicator_A(symbol,start_year)
    if financial_indicator is not None:
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（假设当前文件在 0.1/tools/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 创建完整的文件路径
        filepath = os.path.join(project_root, "data", "financial_statements", f"{symbol}_{start_year}_财务指标.csv")
        print(filepath)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 使用指定目录保存文件
        financial_indicator.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"已保存 financial_indicator 到文件: {filepath}")
    else:
        print(f"跳过保存 financial_indicator，因为数据获取失败")

    return filepath

if __name__ == "__main__":
    financial_indicator_A("002230", "2024")