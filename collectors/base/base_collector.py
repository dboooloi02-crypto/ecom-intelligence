from abc import ABC, abstractmethod
from shared.models import Product


class BaseCollector(ABC):
    """Every platform collector must implement these three methods."""

    @abstractmethod
    def search(self, keyword: str, limit: int = 20) -> list[Product]: ...

    @abstractmethod
    def product(self, product_id: str) -> Product: ...

    @abstractmethod
    def reviews(self, product_id: str, limit: int = 10) -> list[dict]: ...
