"""
Shopee data parser — transforms raw extraction data into clean records.
Works with both extension output (JSON) and CSV exports.
"""
import csv

def parse_extension_output(raw: dict) -> list[dict]:
    products = raw.get("products", [])
    return [{
        "name": (p.get("name") or "").strip()[:200],
        "price": _to_float(p.get("price", 0)),
        "sold": int(p.get("sold", 0)),
        "rating": _to_float(p.get("rating", 0)),
        "shop_location": p.get("shop_location") or p.get("location") or "",
        "stock": int(p.get("stock", 0)),
        "liked_count": int(p.get("liked_count", 0)),
        "source": p.get("_source", "unknown"),
    } for p in products]

def parse_csv(path: str) -> list[dict]:
    products = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            products.append({
                "name": row.get("name") or row.get("商品名") or "",
                "price": _to_float(row.get("price") or row.get("价格") or row.get("售价") or 0),
                "sold": int(_to_float(row.get("sold") or row.get("销量") or row.get("月销") or 0)),
                "rating": _to_float(row.get("rating") or row.get("评分") or 0),
                "shop_location": row.get("shop_location") or row.get("location") or row.get("shop") or row.get("地址") or "",
                "stock": int(_to_float(row.get("stock") or 0)),
                "liked_count": int(_to_float(row.get("liked_count") or row.get("点赞") or 0)),
                "source": "csv",
            })
    return products

def _to_float(val) -> float:
    try: return float(val)
    except (ValueError, TypeError): return 0.0
