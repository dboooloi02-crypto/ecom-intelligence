"""
Rule Scorer — 商品维度评分
"""
from app.shared.models.product import Product

class RuleScorer:
    @staticmethod
    def score(product: Product) -> Product:
        scores = {}
        sold = product.sold
        price = product.price
        rating = product.rating
        scores["demand"] = min(sold / 200, 10) if sold > 0 else 0
        if price > 0:
            if price < 100:
                scores["price_band"] = 8
            elif price < 500:
                scores["price_band"] = 6
            elif price < 1000:
                scores["price_band"] = 4
            else:
                scores["price_band"] = 3
        else:
            scores["price_band"] = 0
        scores["rating_score"] = rating * 2 if rating > 0 else 0
        scores["competition"] = 5
        scores["profit"] = 5
        product.scores = scores
        return product
