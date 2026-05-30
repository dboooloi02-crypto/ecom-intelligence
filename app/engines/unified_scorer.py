"""
Unified Scorer — 融合 Rule + AI 的最终评分
"""
from app.shared.models.product import Product
from app.core.logger import get_logger

log = get_logger("pipeline")

class UnifiedScorer:
    WEIGHTS = {"demand": 0.25, "price_band": 0.15, "rating_score": 0.15, "competition": 0.10, "profit": 0.15, "ai_score": 0.20}
    @staticmethod
    def calculate(product: Product) -> Product:
        scores = product.scores or {}
        TOTAL_RULE_WEIGHT = sum(w for d, w in UnifiedScorer.WEIGHTS.items() if d != "ai_score")
        rule_total = 0.0
        available_weight = 0.0
        for dim, weight in UnifiedScorer.WEIGHTS.items():
            if dim == "ai_score":
                continue
            val = scores.get(dim, 0)
            if val > 0:
                rule_total += val * weight
                available_weight += weight
        coverage = available_weight / TOTAL_RULE_WEIGHT if TOTAL_RULE_WEIGHT > 0 else 0.0
        rule_avg = rule_total / available_weight if available_weight > 0 else 0.0
        ai_score = product.ai_score
        if ai_score is None:
            product.final_score = round(rule_avg, 2)
        else:
            rule_w = 0.80 * coverage
            ai_w = 1.0 - rule_w
            product.final_score = round(rule_avg * rule_w + ai_score * ai_w, 2)
        if product.final_score >= 8:
            product.recommendation = "推荐"
        elif product.final_score >= 5:
            product.recommendation = "观察"
        else:
            product.recommendation = "放弃"
        return product
