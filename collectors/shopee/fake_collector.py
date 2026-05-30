from collectors.base.base_collector import BaseCollector
from shared.models import Product


FAKE_PRODUCTS = {
    "宠物饮水机": [
        Product(title="智能猫狗饮水机 静音水泵 4L大容量", price=599, sales=8340, rating=4.8, reviews=1250, category="宠物饮水"),
        Product(title="无线宠物饮水机 UV杀菌 不锈钢面板", price=899, sales=5210, rating=4.6, reviews=890, category="宠物饮水"),
        Product(title="猫咪循环活水机 过滤棉替换芯 超静音", price=399, sales=12600, rating=4.7, reviews=2100, category="宠物饮水"),
        Product(title="APP智能宠物饮水机 水量监测 远程控制", price=1299, sales=1870, rating=4.5, reviews=340, category="宠物饮水"),
        Product(title="宠物饮水机滤芯 活性炭过滤棉 6片装", price=99, sales=25600, rating=4.9, reviews=4300, category="配件"),
    ],
    "宠物玩具": [
        Product(title="猫玩具电动逗猫棒 自动旋转羽毛", price=249, sales=15300, rating=4.7, reviews=2800, category="猫玩具"),
        Product(title="狗狗发声玩具球 耐咬橡胶 宠物磨牙", price=159, sales=9800, rating=4.5, reviews=1560, category="狗玩具"),
        Product(title="猫咪隧道玩具 折叠式 三入口设计", price=399, sales=6200, rating=4.6, reviews=980, category="猫玩具"),
    ],
    "宠物服饰": [
        Product(title="狗狗雨衣 防水反光条 四脚连体", price=299, sales=7200, rating=4.4, reviews=1100, category="狗服饰"),
        Product(title="猫咪蝴蝶结项圈 可调节 纯棉材质", price=89, sales=18500, rating=4.8, reviews=3200, category="猫服饰"),
    ],
}


class FakeShopeeCollector(BaseCollector):
    def search(self, keyword: str, limit: int = 20) -> list[Product]:
        results = []
        for kw, products in FAKE_PRODUCTS.items():
            if kw in keyword or keyword in kw:
                results.extend(products)
        if not results:
            results = [
                Product(title=f"搜索结果: {keyword} 热销款A", price=499, sales=5000, rating=4.5),
                Product(title=f"搜索结果: {keyword} 高评款B", price=699, sales=3000, rating=4.8),
                Product(title=f"搜索结果: {keyword} 性价比款C", price=299, sales=8000, rating=4.3),
            ]
        return results[:limit]

    def product(self, product_id: str) -> Product:
        return Product(title=f"商品 #{product_id}", price=599, sales=5000)

    def reviews(self, product_id: str, limit: int = 10) -> list[dict]:
        return [{"user": f"用户{i}", "rating": 4.5, "content": "很好用"} for i in range(limit)]
