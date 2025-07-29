from abc import ABC
from dataclasses import dataclass


@dataclass(kw_only=True)
class StateERC721(ABC):
    pool_name: str
    token_id: str
    tick_lower: int
    tick_upper: int
    liquidity: int
