import json
from typing import Any, List

from src.seedwork.adapters.rest import toParamOrders
from src.seedwork.utils.dict import extract


class Orders:
    def __init__(self, keys: List[str]) -> None:
        self.keys = keys

    def __call__(self, orders: Any = {}) -> Any:
        match orders:
            case str():
                try:
                    orders = json.loads(orders)
                except Exception:
                    orders = {}

        plainOrders = extract(orders, self.keys)
        return toParamOrders(plainOrders)
