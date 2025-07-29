from typing import Any, Callable

import numpy as np

from nqs_sdk_extension.mappings import ProtocolTypes
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.run_configuration.protocol_parameters.cex import FakeStateCEX
from nqs_sdk_extension.run_configuration.protocol_parameters.uniswapv3 import FakeStateUniv3
from nqs_sdk_extension.spot.spot_oracle import SpotOracle
from nqs_sdk_extension.state import StateCEX, StateUniv3, TickDataUniv3


def cex_state_helper(state: FakeStateCEX, spot_oracle: SpotOracle) -> StateCEX:
    return StateCEX(
        id=state.id,
        name=state.name,
        block_number=state.block_number,
        block_timestamp=state.block_timestamp,
        numeraire=spot_oracle.numeraire,
    )


def uniswap_state_helper(state: FakeStateUniv3, spot_oracle: SpotOracle) -> StateUniv3:
    if not isinstance(state, FakeStateUniv3):
        return state

    symbol0, symbol1 = state.symbol0, state.symbol1
    initial_spot = spot_oracle.get_selected_spots(
        pairs=[(symbol0, symbol1)], block_timestamp=spot_oracle.current_timestamp
    )[(symbol0, symbol1)]
    sqrt_price_x96 = TickMath.price_to_sqrt_price_x96(initial_spot, state.decimals0, state.decimals1)
    initial_balance0, initial_balance1 = state.initial_balance0, state.initial_balance1
    if initial_balance0 is not None:
        liquidity = (initial_balance0 * np.sqrt(initial_spot)) * (10 ** (0.5 * (state.decimals0 + state.decimals1)))
    elif initial_balance1 is not None:
        liquidity = (initial_balance1 / np.sqrt(initial_spot)) * (10 ** (0.5 * (state.decimals0 + state.decimals1)))
    else:
        raise KeyError("Initial balance unit must be either token0 or token1")
    liquidity = int(liquidity)

    tick0 = TickDataUniv3(
        liquidity_gross=liquidity,
        liquidity_net=liquidity,
        fee_growth_outside_0_x128=0,
        fee_growth_outside_1_x128=0,
        tick_idx=-887272,
    )
    tick1 = TickDataUniv3(
        liquidity_gross=liquidity,
        liquidity_net=-1 * liquidity,
        fee_growth_outside_0_x128=0,
        fee_growth_outside_1_x128=0,
        tick_idx=887272,
    )

    return StateUniv3(
        id=state.id,
        name=state.name,
        block_number=state.block_number,
        block_timestamp=state.block_timestamp,
        symbol0=state.symbol0,
        symbol1=state.symbol1,
        token0=state.token0,
        token1=state.token1,
        decimals0=state.decimals0,
        decimals1=state.decimals1,
        fee_tier=state.fee_tier,
        liquidity=liquidity,
        sqrt_price_x96=sqrt_price_x96,
        fee_growth_global_0_x128=0,
        fee_growth_global_1_x128=0,
        tick=TickMath.price_to_tick(initial_spot, state.decimals0, state.decimals1),
        ticks=[tick0, tick1],
    )


mapping_type_to_state_helper: dict[str, Callable[[Any, Any], Any]]
mapping_type_to_state_helper = {
    ProtocolTypes.COMPOUND_V2.value: lambda state, oracle: state,
    ProtocolTypes.UNISWAP_V3.value: uniswap_state_helper,
    ProtocolTypes.CEX.value: cex_state_helper,
}
