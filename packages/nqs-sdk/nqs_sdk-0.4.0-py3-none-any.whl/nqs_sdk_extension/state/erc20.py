from dataclasses import dataclass

from nqs_sdk_extension.state import ABCProtocolState


@dataclass
class StateERC20(ABCProtocolState):
    symbol: str
    address: str
    decimals: int
    total_supply: int | None = None
