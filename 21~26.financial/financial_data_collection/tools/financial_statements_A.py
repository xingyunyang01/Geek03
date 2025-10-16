import akshare as ak
import pandas as pd
from typing import Dict, Optional
from langchain_core.tools import tool
import os

@tool
def get_balance_sheet_A(stock_code: str = "SH600600", year: str = "2024"):
    """
    获取沪深A股公司的资产负债表，并保存到文件中
    
    Args:
        stock_code (str): 带市场标识的股票代码，如SH600600，SZ000001等
        year (str): 报告年份，如2024
    
    Returns:
        filepath(str): 资产负债表的保存路径
    """
    try:  
        df_balance_sheet = ak.stock_balance_sheet_by_yearly_em(symbol=stock_code)
        print(df_balance_sheet.dtypes)
        # 只取REPORT_DATE是2024-12-31的数据
        df_balance_sheet = df_balance_sheet[df_balance_sheet['REPORT_DATE'] == f'{year}-12-31 00:00:00']
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（假设当前文件在 0.1/tools/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 去掉SH,SZ前缀
        stock_code_clean = stock_code[2:] if stock_code.startswith(('SH', 'SZ')) else stock_code
        # 创建完整的文件路径
        filepath = os.path.join(project_root, "data", "financial_statements", f"{stock_code_clean}_{year}_资产负债表.csv")
        print(filepath)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 使用指定目录保存文件
        df_balance_sheet.to_csv(filepath, index=False, encoding='utf-8-sig')

        return filepath
    except Exception as e:
        print(f"获取资产负债表失败: {e}")
        return ""


@tool
def get_income_statement_A(stock_code: str = "SH600600", year: str = "2024"):
    """    
    获取沪深A股公司的利润表，并保存到文件中
    
    Args:
        stock_code (str): 带市场标识的股票代码，如SH600600，SZ000001等
        year (str): 报告年份，如2024
    Returns:
        filepath(str): 利润表的保存路径
    """
    try:
        df_income_statement = ak.stock_profit_sheet_by_yearly_em(symbol=stock_code)
        # 只取REPORT_DATE是2024-12-31的数据
        df_income_statement = df_income_statement[df_income_statement['REPORT_DATE'] == f'{year}-12-31 00:00:00']
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（假设当前文件在 0.1/tools/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 去掉SH,SZ前缀
        stock_code_clean = stock_code[2:] if stock_code.startswith(('SH', 'SZ')) else stock_code
        # 创建完整的文件路径
        filepath = os.path.join(project_root, "data", "financial_statements", f"{stock_code_clean}_{year}_利润表.csv")
        print(filepath)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 使用指定目录保存文件
        df_income_statement.to_csv(filepath, index=False, encoding='utf-8-sig')

        return filepath
    
    except Exception as e:
        print(f"获取利润表失败: {e}")
        return ""

@tool
def get_cash_flow_statement_A(stock_code: str = "SH600600", year: str = "2024"):
    """
    获取沪深A股公司的现金流量表，并保存到文件中
    
    Args:
        stock_code (str): 带市场标识的股票代码，如SH600600，SZ000001等
        year (str): 报告年份，如2024
    Returns:
        filepath(str): 现金流量表的保存路径
    """
    try:
        df_cash_flow = ak.stock_cash_flow_sheet_by_yearly_em(symbol=stock_code)
        # 只取REPORT_DATE是2024-12-31的数据
        df_cash_flow = df_cash_flow[df_cash_flow['REPORT_DATE'] == f'{year}-12-31 00:00:00']
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（假设当前文件在 0.1/tools/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 去掉SH,SZ前缀
        stock_code_clean = stock_code[2:] if stock_code.startswith(('SH', 'SZ')) else stock_code
        # 创建完整的文件路径
        filepath = os.path.join(project_root, "data", "financial_statements", f"{stock_code_clean}_{year}_现金流量表.csv")
        print(filepath)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 使用指定目录保存文件
        df_cash_flow.to_csv(filepath, index=False, encoding='utf-8-sig')

        return filepath
    
    except Exception as e:
        print(f"获取现金流量表失败: {e}")
        return ""
