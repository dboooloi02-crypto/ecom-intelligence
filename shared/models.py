from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    title: str
    price: float
    currency: str = "TWD"
    sales: int = 0
    rating: float = 0.0
    reviews: int = 0
    url: str = ""
    platform: str = "shopee"
    category: str = ""
    image_url: str = ""
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def dict(self):
        return asdict(self)


@dataclass
class ResearchQuery:
    raw: str
    market: str = ""
    category: str = ""
    keywords: list[str] = field(default_factory=list)
    platform: str = "all"


@dataclass
class ResearchReport:
    query: str
    summary: str
    market_size: str = ""
    hot_products: list[dict] = field(default_factory=list)
    competition: str = ""
    risks: str = ""
    recommendation: str = ""
    score: float = 0.0
    sources: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrendPoint:
    product_id: str
    date: str
    sales: int
    price: float
    rating: float
