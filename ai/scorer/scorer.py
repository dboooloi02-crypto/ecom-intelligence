import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    from zhipuai import ZhipuAI
    HAS_ZHIPU = True
except ImportError:
    HAS_ZHIPU = False

API_KEY = "ef24bd9566a64e46a562ee602f4e29a1.ie48kBJSpGwoXkz4"

SCORE_PROMPT = """你是一个跨境电商选品专家。分析这个产品，输出JSON评分。

产品：{title}
价格：{price}
销量：{sales}
评分：{rating}
平台：{platform}

评分维度（0-10）：
1. demand_score: 市场需求强度
2. competition_score: 竞争度（越高越好=竞争小）
3. profit_score: 利润空间
4. trend_score: 增长趋势
5. overall: 综合推荐指数

输出JSON：
{{
  "demand_score": 0-10,
  "competition_score": 0-10,
  "profit_score": 0-10,
  "trend_score": 0-10,
  "overall": 0-10,
  "reason": "一句话推荐理由"
}}
"""


class Scorer:
    def __init__(self):
        self.client = ZhipuAI(api_key=API_KEY)

    def score_product(self, product: dict) -> dict:
        try:
            resp = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": SCORE_PROMPT.format(**product)}],
                temperature=0.3, max_tokens=300, response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            return {"demand_score": 5, "competition_score": 5, "profit_score": 5, "trend_score": 5, "overall": 5, "reason": f"评分失败: {e}"}

    def score_batch(self, products: list[dict]) -> list[dict]:
        results = []
        for p in products:
            scores = self.score_product(p)
            results.append({**p, **scores})
        return results


class MockScorer:
    def score_batch(self, products: list[dict]) -> list[dict]:
        results = []
        for p in products:
            sales = p.get("sales", 0) or 0
            rating = p.get("rating", 0) or 0
            demand = min(10, max(1, sales / 2000))
            competition = min(10, max(1, 10 - sales / 5000))
            profit = min(10, max(1, (p.get("price", 0) or 0) / 200))
            trend = min(10, max(1, rating * 1.5))
            overall = round((demand * 0.3 + competition * 0.2 + profit * 0.25 + trend * 0.25), 1)
            results.append({
                **p,
                "demand_score": round(demand, 1), "competition_score": round(competition, 1),
                "profit_score": round(profit, 1), "trend_score": round(trend, 1),
                "overall": overall,
                "reason": f"销量{sales}+评分{rating}" if sales > 0 else "数据不足",
            })
        return results
