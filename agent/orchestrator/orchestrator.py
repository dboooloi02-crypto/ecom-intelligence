import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from collectors.shopee.fake_collector import FakeShopeeCollector
from ai.scorer.scorer import MockScorer
from ai.report.report_generator import ReportGenerator
from shared.models import ResearchReport


class EcomAgent:
    def __init__(self):
        self.collector = FakeShopeeCollector()
        self.scorer = MockScorer()
        self.reporter = ReportGenerator()

    def research(self, query: str) -> ResearchReport:
        keywords = self._parse_query(query)
        all_products = []
        seen = set()
        for kw in keywords:
            products = self.collector.search(kw, limit=20)
            for p in products:
                if p.title not in seen:
                    seen.add(p.title)
                    all_products.append(p)
        if not all_products:
            return ResearchReport(query=query, summary=f"未找到「{query}」相关产品数据。", recommendation="建议更换关键词或扩大搜索范围")
        scored = self.scorer.score_batch([p.dict() for p in all_products])
        report = self.reporter.generate(query, [p.dict() for p in all_products], scored)
        return report

    def _parse_query(self, query: str) -> list[str]:
        for prefix in ["帮我找", "分析", "研究", "搜索", "找", "看看"]:
            query = query.replace(prefix, "")
        import re
        keywords = re.split(r'[，、和与及市场]', query)
        keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]
        if not keywords:
            keywords = [query.strip()]
        return keywords
