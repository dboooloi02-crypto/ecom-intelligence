"""
Product 数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Product:
    title: str = ""
    price: float = 0
    sold: int = 0
    rating: float = 0
    shop: str = ""
    platform: str = ""
    keyword: str = ""
    url: str = ""
    source_tag: str = ""
    collected_at: str = ""
    demand_score: float = 0
    competition_score: float = 0
    profit_score: float = 0
    ai_score: Optional[float] = None
    ai_summary: str = ""
    pain_points: List[str] = field(default_factory=list)
    evidence: List[dict] = field(default_factory=list)
    final_score: float = 0
    recommendation: str = ""
    raw_data: dict = field(default_factory=dict)
    scores: dict = field(default_factory=dict)
    ai_analysis: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat()
