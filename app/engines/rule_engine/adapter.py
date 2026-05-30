"""
Rule Engine Adapter — CSV行 → Product
"""
from app.shared.models.product import Product

class RuleEngineAdapter:
    @staticmethod
    def from_csv_row(row: dict) -> Product:
        return Product(
            title=row.get("title", "")[:120],
            price=float(str(row.get("price", 0)).replace(",", "")),
            sold=int(float(str(row.get("sold", 0)).replace(",", ""))),
            rating=float(str(row.get("rating", 0)).replace(",", "")),
            shop=row.get("shop", ""),
            platform="shopee",
            url=row.get("url", ""),
        )
