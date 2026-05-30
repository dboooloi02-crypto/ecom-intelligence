"""
Report Generator
"""
from app.shared.models.market_report import MarketReport

class ReportGenerator:
    @staticmethod
    def from_market(report: MarketReport) -> dict:
        return {"keyword": report.keyword, "market_score": report.market_score, "summary": report.summary, "example_products": report.example_products}
