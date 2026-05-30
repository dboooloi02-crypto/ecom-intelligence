"""
AI Scorer — 将 AI 响应转为 MarketReport
"""
from app.shared.models.market_report import MarketReport
from app.shared.models.product import Product

class AIScorer:
    @staticmethod
    def build_report(ai_result: dict) -> MarketReport:
        products = []
        for ex in ai_result.get("example_products", []):
            p = Product(title=ex.get("title", ""), price=float(ex.get("price", 0)), sold=int(ex.get("sold", 0)))
            p.keyword = ai_result.get("keyword", "")
            products.append(p)
        report = MarketReport(
            keyword=ai_result.get("keyword", ""),
            market_score=ai_result.get("market_score", 0),
            summary=ai_result.get("summary", ""),
            demand=ai_result.get("demand", ""),
            competition=ai_result.get("competition", ""),
            profit=ai_result.get("profit", ""),
            pain_points=ai_result.get("pain_points", []),
            opportunities=ai_result.get("opportunities", []),
            risks=ai_result.get("risks", []),
            evidence=ai_result.get("evidence", []),
            example_products=products,
        )
        return report
