from dataclasses import dataclass
from typing import TypeAlias

# Events
# https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents

# Type aliases
int24: TypeAlias = int
uint128: TypeAlias = int
uint256: TypeAlias = int
int256: TypeAlias = int
uint160: TypeAlias = int


@dataclass
class Swap:
    block_number: int
    block_timestamp: int
    amount0: int256
    amount1: int256
    zero_for_one: bool
    fee_amount: int256
    sqrt_price_x96: uint160
    liquidity: uint128
    tick: int24


@dataclass
class Mint:
    block_number: int
    block_timestamp: int
    tick_lower: int24
    tick_upper: int24
    amount: uint128
    amount0: uint256
    amount1: uint256
    sqrt_price_x96: uint160


@dataclass
class Burn:
    block_number: int
    block_timestamp: int
    tick_lower: int24
    tick_upper: int24
    amount: uint128
    amount0: uint256
    amount1: uint256


@dataclass
class Collect:
    token_id: str
    block_number: int
    block_timestamp: int
    tick_lower: int24
    tick_upper: int24
    amount0: uint256
    amount1: uint256


@dataclass
class Update:
    token_id: str
    block_number: int
    block_timestamp: int
    delta_amount: int
    sqrt_price_x96: int


@dataclass
class Create:
    token_id: str
    tick_lower: int
    tick_upper: int
    block_number: int
    block_timestamp: int
    amount: int
    sqrt_price_x96: int
