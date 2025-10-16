from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


import operator


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    stock_code: str
    market: str
    stock_name: str
    final_report: Dict[str, Any]