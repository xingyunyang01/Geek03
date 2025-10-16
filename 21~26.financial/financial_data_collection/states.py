from typing import TypedDict, List
from langgraph.graph import add_messages
from typing_extensions import Annotated
from schemas import CompetitorInfoList

class OverallState(TypedDict):
    stock_code: str
    stock_name: str
    market: str
    year: str