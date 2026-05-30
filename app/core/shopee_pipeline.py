"""
Shopee Pipeline — 直连 API 数据流
"""
import logging
from app.core.shopee_client import ShopeeClient
from app.pipelines.csv_pipeline import CSVPipeline

log = logging.getLogger(__name__)

class ShopeePipeline:
    def __init__(self):
        self.client = ShopeeClient()
        self.csv_pipeline = CSVPipeline()
    def run(self, keyword: str, progress_cb=None) -> list:
        def step(msg):
            if progress_cb:
                progress_cb(msg)
        raw_items = self.client.search(keyword, progress_cb=progress_cb)
        if not raw_items:
            step("⚠️ 未获取到商品数据")
            return []
        step(f"⚙️ 计算 {len(raw_items)} 个商品评分...")
        rows = [{"title": item["title"], "price": str(item["price"]), "sold": str(item["sold"]), "rating": str(item["rating"]), "shop": item.get("shop", ""), "url": item.get("url", "")} for item in raw_items]
        products = self.csv_pipeline.run(rows)
        for product, item in zip(products, raw_items):
            product.source_tag = "shopee_realtime"
            if not getattr(product, "url", None):
                product.url = item.get("url", "")
        step(f"✅ 完成，共 {len(products)} 个商品")
        return products
