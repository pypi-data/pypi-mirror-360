from dataclasses import dataclass, field

from nqs_pycore import LPTokenUniv3

from nqs_sdk_extension.state import ABCProtocolState

"""
    Dataclasses for Uniswap V3.
    The field names are in general the same as in the Uniswap V3 smart contracts.
    TheGraph data: https://github.com/Uniswap/v3-subgraph/blob/main/schema.graphql
"""


# TODO: add field converters (so that we do not need to convert to int in the generator or in the protocol)


@dataclass(kw_only=True)
class TickDataUniv3:
    liquidity_gross: int
    liquidity_net: int
    fee_growth_outside_0_x128: int
    fee_growth_outside_1_x128: int
    tick_idx: int  # redundant with the key of the SortedDict


@dataclass(kw_only=True)
class StateUniv3(ABCProtocolState):
    token0: str
    token1: str
    symbol0: str
    symbol1: str
    decimals0: int
    decimals1: int
    fee_tier: int  # fee amount
    liquidity: int  # in range liquidity
    sqrt_price_x96: int  # current price tracker
    fee_growth_global_0_x128: int  # tracker for global fee growth
    fee_growth_global_1_x128: int  # tracker for global fee growth
    tick: int  # current tick
    ticks: list[TickDataUniv3] = field(repr=False)


if __name__ == "__main__":
    tick1 = TickDataUniv3(
        liquidity_gross=100, liquidity_net=100, fee_growth_outside_0_x128=0, fee_growth_outside_1_x128=0, tick_idx=100
    )
    tick2 = TickDataUniv3(
        liquidity_gross=100, liquidity_net=-100, fee_growth_outside_0_x128=0, fee_growth_outside_1_x128=0, tick_idx=200
    )
    print(tick1, tick2)
    state = StateUniv3(
        id=0,
        name="Uniswap V3",
        block_number=0,
        block_timestamp=0,
        token0="0x0",
        token1="0x1",
        symbol0="ETH",
        symbol1="USDC",
        decimals0=18,
        decimals1=6,
        fee_tier=500,
        liquidity=100,
        sqrt_price_x96=100,
        fee_growth_global_0_x128=0,
        fee_growth_global_1_x128=0,
        tick=150,
        ticks=[tick1, tick2],
    )
    print(state)
    lp_token = LPTokenUniv3(
        pool_name="pool0",
        token_id="1",
        tick_lower=100,
        tick_upper=200,
        liquidity=100,
        fee_growth_inside_0_last_x128=0,
        fee_growth_inside_1_last_x128=0,
        tokens_owed_0=0,
        tokens_owed_1=0,
    )
    print(lp_token)
