import os
import akshare as ak
import pandas as pd
from typing import Dict, Optional
from langchain_core.tools import tool

@tool
def get_stock_intro(symbol: str = "000066") -> Optional[str]:
    """
    获取股票的基本介绍信息，包括主营业务、经营范围等。
    :param symbol: 股票代码（如 '000066'、'00700'）
    :return: 返回pandas表格的字符串，若获取失败则返回None
    """

    # 去掉A股代码的SH/SZ前缀
    clean_symbol = symbol.replace('SH', '').replace('SZ', '')
    try:
        df = ak.stock_zyjs_ths(symbol=clean_symbol)
        if df is not None and not df.empty:
            return df.to_string(index=False)
    except Exception as e:
        print(f"AkShare A股获取失败 ({clean_symbol}): {e}")
        return None      # 港股
    
    return None