"""
AI Product Scorer — DSPy + mock modes.
"""
import os
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

if DSPY_AVAILABLE:
    class ProductScore(dspy.Signature):
        product_name = dspy.InputField(desc="Product title from Shopee")
        price = dspy.InputField(desc="Product price")
        sales = dspy.InputField(desc="Number sold")
        rating = dspy.InputField(desc="Rating (1.0-5.0)")
        score = dspy.OutputField(desc="Score 1-10")
        recommendation = dspy.OutputField(desc="yes/no/watch")
        reason = dspy.OutputField(desc="Chinese reason, max 50 chars")

    class ProductScorer(dspy.Module):
        def __init__(self):
            super().__init__()
            self.scorer = dspy.ChainOfThought(ProductScore)
        def forward(self, product_name, price, sales, rating):
            return self.scorer(product_name=product_name, price=str(price), sales=str(sales), rating=str(rating))

def mock_score(product: dict) -> dict:
    name = (product.get("name") or "").lower()
    price = float(product.get("price", 0))
    sold = int(product.get("sold", 0))
    rating = float(product.get("rating", 0))
    score = 5.0
    reasons = []
    if 10 < price < 50:
        score += 1.5; reasons.append("价格区间好")
    elif price <= 5:
        score -= 1; reasons.append("单价过低")
    elif price >= 200:
        score -= 0.5; reasons.append("单价偏高")
    if sold > 1000:
        score += 2; reasons.append("爆款")
    elif sold > 200:
        score += 1; reasons.append("热销中")
    elif sold < 10:
        score -= 0.5; reasons.append("销量不足")
    if rating >= 4.5:
        score += 1; reasons.append("评分高")
    elif rating < 3.5 and rating > 0:
        score -= 1; reasons.append("评分低")
    for kw in ["蓝牙", "无线", "便携", "收纳", "充电", "智能"]:
        if kw in name:
            score += 0.5; reasons.append("热词匹配")
            break
    score = max(1, min(10, round(score, 1)))
    rec = "yes" if score >= 7 else ("watch" if score >= 5 else "no")
    return {"score": score, "recommendation": rec, "reason": " | ".join(reasons) if reasons else "数据正常"}

def score_product(product: dict, use_mock: bool = False) -> dict:
    if use_mock or not DSPY_AVAILABLE:
        return mock_score(product)
    try:
        lm = dspy.OpenAI(model="glm-4-flash", api_key=os.getenv("ZHIPU_API_KEY",""), api_base=os.getenv("ZHIPU_API_BASE","https://open.bigmodel.cn/api/paas/v4"), max_tokens=200, temperature=0.3)
        dspy.configure(lm=lm)
        r = ProductScorer().forward(product_name=product.get("name",""), price=str(product.get("price",0)), sales=str(product.get("sold",0)), rating=str(product.get("rating",0)))
        return {"score": float(r.score), "recommendation": r.recommendation, "reason": r.reason}
    except Exception:
        return mock_score(product)

def score_products(products: list[dict], use_mock: bool = False) -> list[dict]:
    results = [{**p, **score_product(p, use_mock=use_mock)} for p in products]
    results.sort(key=lambda r: r.get("score", 0), reverse=True)
    return results
