from pydantic import BaseModel
from typing import List

class CompetitorInfo(BaseModel):
    stock_code: str
    stock_name: str
    market: str

class CompetitorInfoList(BaseModel):
    competitors: List[CompetitorInfo]