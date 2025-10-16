from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, Dict, List, Any

from langgraph.graph import add_messages
from langgraph.types import Send
from typing_extensions import Annotated
from schemas import CompetitorInfoList

import operator


class OverallState(TypedDict):
    stock_code: str
    stock_name: str
    market: str
    messages: Annotated[list, add_messages]
    competitor_and_industry_data: str
    competitor_info: CompetitorInfoList
    year: list[str]
    company_report: Dict[str, Any]
    compare_company_report: Dict[str, Any]
    shareholder_info: str
    valuation_model: str
    business_info: str
    formatted_output: List[str]
    final_report: str