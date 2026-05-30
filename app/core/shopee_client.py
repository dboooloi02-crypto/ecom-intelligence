"""
Shopee Client — 直连 Shopee 台湾站搜索 API
"""
import logging
import requests

log = logging.getLogger(__name__)

class ShopeeClient:
    SEARCH_URL = "https://shopee.tw/api/v4/search/search_items"
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36", "Referer": "https://shopee.tw/", "X-API-SOURCE": "pc", "Accept": "application/json"}
    PRICE_DIVISOR = 100_000
    def search(self, keyword: str, limit: int = 60, progress_cb=None) -> list[dict]:
        def step(msg):
            if progress_cb:
                progress_cb(msg)
        step(f"📡 请求 Shopee API：{keyword}")
        params = {"keyword": keyword, "limit": min(limit, 60), "newest": 0, "order": "desc", "sortby": "relevancy"}
        try:
            resp = requests.get(self.SEARCH_URL, params=params, headers=self.HEADERS, timeout=12)
            resp.raise_for_status()
        except requests.Timeout:
            raise RuntimeError("Shopee API 超时")
        except requests.HTTPError as e:
            raise RuntimeError(f"Shopee API 返回 {e.response.status_code}")
        except requests.ConnectionError:
            raise RuntimeError("无法连接 Shopee")
        raw = resp.json()
        items = raw.get("items") or []
        if not items:
            if "error" in raw or raw.get("error_msg"):
                raise RuntimeError(f"Shopee 拒绝请求：{raw.get('error_msg', '未知错误')}")
        step(f"✅ 获取 {len(items)} 条商品数据")
        return [self._parse(i) for i in items if i]
    def _parse(self, item: dict) -> dict:
        m = item.get("item_basic") or item
        raw_price = m.get("price") or m.get("price_min") or 0
        return {"title": (m.get("name") or "")[:120], "price": round(raw_price / self.PRICE_DIVISOR, 0), "sold": m.get("historical_sold") or m.get("sold") or 0, "rating": round((m.get("item_rating") or {}).get("rating_star") or 0, 1), "shop": m.get("shop_name") or "", "url": self._build_url(m), "source_tag": "shopee_realtime"}
    def _build_url(self, m: dict) -> str:
        shop_id = m.get("shopid") or m.get("shop_id")
        item_id = m.get("itemid") or m.get("item_id")
        if shop_id and item_id:
            return f"https://shopee.tw/product/{shop_id}/{item_id}"
        return ""
