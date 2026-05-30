"""
CSV Pipeline — CSV行 → Product → 评分
"""
from typing import List
from app.shared.models.product import Product
from app.engines.rule_engine.adapter import RuleEngineAdapter
from app.engines.rule_engine.scorer import RuleScorer
from app.engines.unified_scorer import UnifiedScorer

class CSVPipeline:
    @staticmethod
    def run(rows: List[dict]) -> List[Product]:
        products = []
        for row in rows:
            product = RuleEngineAdapter.from_csv_row(row)
            product = RuleScorer.score(product)
            product = UnifiedScorer.calculate(product)
            products.append(product)
        return products
