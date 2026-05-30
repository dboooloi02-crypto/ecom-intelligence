"""
MarketReport 数据模型
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class MarketReport:
    keyword: str = ""
    market_score: float = 0
    summary: str = ""
    demand: str = ""
    competition: str = ""
    profit: str = ""
    pain_points: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    evidence: List[dict] = field(default_factory=list)
    example_products: list = field(default_factory=list)
