import os
import akshare as ak
import pandas as pd
from typing import Dict, Optional
from langchain_core.tools import tool

# 根据 输入获取代码，因为AI有时候会直接把 名称放进去执行
def get_symbol(input):
    if "SZ" in input:
        input=input.replace("SZ","")
    if  "SH" in input:
        input=input.replace("SH","")
    if "sz" in input:
        input=input.replace("sz","")
    if  "sh" in input:
        input=input.replace("sh","")

    if input.isdigit():
        return input
    else:
        df=ak.stock_zh_a_spot_em()
        df=df[df["名称"].str.contains(input)]
        return df["代码"].values[0]

def format_df(df, decimal_places=2):
    if df.empty:
        return "没有找到相关股票的数据"
    formatted_lines = []
    for _, row in df.iterrows():
        line_parts = []
        for col in df.columns:
            value = row[col]
            # 处理缺失值
            formatted_value = value if pd.notna(value)  else ''
            # 根据数据类型调整格式
            if isinstance(formatted_value, (int, float)):
                formatted_value = f"{formatted_value:.{decimal_places}f}"
            line_parts.append(f"{col}:{formatted_value}")
        # 合并当前行的字符串
        formatted_line = "\n".join(line_parts)
        formatted_lines.append(formatted_line)
    # 行间保留空行
    return "\n\n".join(formatted_lines)

@tool
def ak_stock_gdfx_top_10(symbol:str):
    """
    根据股票代码获取该股票的十大股东信息（仅包含沪深A股股票），并保存到文件中
    Args:
        symbol: 带市场标识的股票代码,如:sh688686
    Return:
        filepath(str): 十大股东信息的保存路径
    """
    df = ak.stock_gdfx_top_10_em(symbol=symbol, date="20250331")
    # 在DataFrame前添加标题行
    # 创建一个只包含标题的单行DataFrame
    title_row = pd.DataFrame([['十大股东信息'] + [''] * (len(df.columns) - 1)], columns=df.columns)
    # 将标题行和原数据合并，保持原表结构不变
    df_with_title = pd.concat([title_row, df], ignore_index=True)
    
    return df_with_title

@tool
def ak_stock_gdfx_free_top_10(symbol:str):
    """
    根据股票代码获取该股票的十大流通股东信息（仅包含沪深A股股票），并保存到文件中
    
    Args:
        symbol: 带市场标识的股票代码,如:sh688686
    Return:
        filepath(str): 十大流通股东信息的保存路径
    """
    df = ak.stock_gdfx_free_top_10_em(symbol=symbol,date="20250331")
    # 在DataFrame前添加标题行
    # 创建一个只包含标题的单行DataFrame
    title_row = pd.DataFrame([['十大流通股东信息'] + [''] * (len(df.columns) - 1)], columns=df.columns)
    # 将标题行和原数据合并，保持原表结构不变
    df_with_title = pd.concat([title_row, df], ignore_index=True)

    return df_with_title

@tool
def ak_stock_main_stock_holder(symbol:str):
    """
    根据股票代码获取该股票的主要股东信息（仅包含沪深A股股票），并保存到文件中
    Args:
        symbol: 股票代码,如:688686
    Return:
        filepath(str): 主要股东信息的保存路径
    """
    df = ak.stock_main_stock_holder(stock=symbol)
    
    # 在DataFrame前添加标题行
    # 创建一个只包含标题的单行DataFrame
    title_row = pd.DataFrame([['主要股东信息'] + [''] * (len(df.columns) - 1)], columns=df.columns)
    # 将标题行和原数据合并，保持原表结构不变
    df_with_title = pd.concat([title_row, df], ignore_index=True)
    
    return df_with_title

@tool
def ak_stock_restricted_release_queue_sina(symbol:str):
    """
    根据股票代码获取该股票的限售解禁信息（仅包含沪深A股股票）
    Args:
        symbol: 股票代码,如:688686
    Return:
        filepath(str): 限售解禁信息的保存路径
    """
    df = ak.stock_restricted_release_queue_sina(symbol=symbol)
    # 在DataFrame前添加标题行
    # 创建一个只包含标题的单行DataFrame
    title_row = pd.DataFrame([['限售解禁信息'] + [''] * (len(df.columns) - 1)], columns=df.columns)
    # 将标题行和原数据合并，保持原表结构不变
    df_with_title = pd.concat([title_row, df], ignore_index=True)

    return df_with_title