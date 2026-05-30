import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.models import ResearchReport


class ReportGenerator:
    def generate(self, query: str, products: list[dict], scores: list[dict]) -> ResearchReport:
        if not products:
            return ResearchReport(query=query, summary=f"未找到「{query}」相关产品数据。", recommendation="建议更换关键词或平台")
        sorted_items = sorted(scores, key=lambda x: x.get("overall", 0), reverse=True)
        top = sorted_items[:5]
        total_sales = sum(p.get("sales", 0) or 0 for p in products)
        avg_price = sum(p.get("price", 0) or 0 for p in products) / len(products)
        avg_rating = sum(p.get("rating", 0) or 0 for p in products) / len(products)

        hot_products = []
        for i, p in enumerate(top[:5]):
            hot_products.append({"rank": i+1, "title": p.get("title", ""), "price": p.get("price", 0), "sales": p.get("sales", 0), "rating": p.get("rating", 0), "overall": p.get("overall", 0), "reason": p.get("reason", "")})

        best = top[0] if top else {}
        summary = f"📊 「{query}」市场分析\n共找到 {len(products)} 款相关产品，总销量约 {total_sales:,} 件，平均售价 ¥{avg_price:.0f}，平均评分 {avg_rating:.1f}。"
        if best:
            summary += f"\n\n🏆 推荐产品：{best.get('title', '')} (综合分 {best.get('overall', 0)}/10)\n  售价 ¥{best.get('price', 0)} | 已售 {best.get('sales', 0):,} 件 | 评分 {best.get('rating', 0)}"

        competition = f"市场热度：{'🔥' if total_sales > 10000 else '⭐'} (总销量 {total_sales:,})\n价格区间：¥{min(p.get('price',0) or 0 for p in products):.0f} - ¥{max(p.get('price',0) or 0 for p in products):.0f}\n平均售价：¥{avg_price:.0f}"
        rec = f"推荐指数：{best.get('overall', 0) if best else 0}/10\n"
        if best:
            rec += f"推荐理由：{best.get('reason', '')}"

        return ResearchReport(query=query, summary=summary, market_size=f"采集到 {len(products)} 个商品样本", hot_products=hot_products, competition=competition, recommendation=rec, score=best.get("overall", 0) if best else 0, sources=["Shopee 模拟数据（待接入真实数据源）"])

    def to_markdown(self, report: ResearchReport) -> str:
        md = f"# 📊 跨境研究报告：{report.query}\n\n## 摘要\n{report.summary}\n\n## 市场规模\n{report.market_size}\n\n## 热门产品 TOP5\n"
        for p in report.hot_products:
            md += f"\n### #{p['rank']} {p['title']}\n- 售价：¥{p['price']} | 已售 {p['sales']:,} 件 | 评分 {p['rating']}\n- 综合评分：{p['overall']}/10\n- 推荐理由：{p['reason']}\n"
        md += f"\n## 竞争分析\n{report.competition}\n\n## 推荐\n{report.recommendation}\n\n---\n*\u751f成时间：{report.generated_at}*\n*数据来源：{', '.join(report.sources)}*"
        return md
