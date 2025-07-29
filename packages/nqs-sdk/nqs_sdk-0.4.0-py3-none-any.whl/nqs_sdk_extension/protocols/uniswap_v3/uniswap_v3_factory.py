from typing import List, Tuple

import numpy as np
from nqs_pycore import MutBuilderSharedState, SimulationTime

from nqs_sdk.core.protocol_registry.decorators import protocol_factory
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk_extension.generator.historical.dataquasar.uniswap_v3 import DTQUniswapV3Generator
from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.generator.random.uniswapv3 import RandomUniv3Generator
from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk_extension.protocols.common.historical_tx_generator import HistoricalTxGenerator
from nqs_sdk_extension.protocols.common.random_tx_generator import RandomTxGenerator
from nqs_sdk_extension.protocols.uniswap_v3.uniswap_v3_protocol import UniswapV3Wrapper
from nqs_sdk_extension.protocols.util import get_all_tokens
from nqs_sdk_extension.run_configuration.protocol_parameters.uniswapv3 import (
    FakeStateUniv3,
    Uniswapv3ProtocolInformation,
)
from nqs_sdk_extension.spot.spot_oracle import SpotOracle
from nqs_sdk_extension.state import StateUniv3, TickDataUniv3

from .uniswap_v3_arbitrager import UniswapV3Arbitrager

UNISWAP_V3_ID = "uniswap_v3"


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


class Count:
    count = 0


@protocol_factory()
class UniswapV3Factory(ProtocolFactory):
    def __init__(self, need_generator: bool = False) -> None:
        self.need_generator = need_generator

    def id(self) -> str:
        return UNISWAP_V3_ID

    def build(
        self,
        time: SimulationTime,
        builder_state: MutBuilderSharedState,
        common_config: dict,
        backtest: bool,
        config: dict,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        protocols: List[Protocol] = []
        generators: List[TxGenerator] = []

        if backtest:
            for pool in config.get("pools", []):
                protocol, generator = build_historical_state(time, builder_state, pool)
                protocols.append(protocol)
                generators.append(generator)
        else:
            initial_state = config.get("initial_state", {})
            for hist in initial_state.get("historical_state", {}).get("pools", []):
                protocol, _ = build_historical_state(time, builder_state, hist)
                protocols.append(protocol)
            for hist in initial_state.get("custom_state", {}).get("pools", []):
                protocols.append(build_simulation_state(time, builder_state, hist))

            wrapper_map = {wrapper.name: wrapper for wrapper in protocols if isinstance(wrapper, UniswapV3Wrapper)}

            for rand in config.get("random_generation_params", {}).get("pools", []):
                pool_name = rand["pool_name"]
                if pool_name in wrapper_map:
                    wrapper = wrapper_map[pool_name]
                    generators.append(build_random_generator(rand, wrapper.protocol, time))

        if protocols:
            interval = int(common_config.get("arbitrage_block_frequency", 0))
            if interval > 0:
                generators.append(UniswapV3Arbitrager(time, [p.id() for p in protocols], interval))

        return protocols, generators


def build_historical_state(
    time: SimulationTime, builder_state: MutBuilderSharedState, protocol_info: dict
) -> Tuple[UniswapV3Wrapper, HistoricalTxGenerator]:
    Count.count += 1
    name = protocol_info["pool_name"]
    generator = DTQUniswapV3Generator(Count.count, name, protocol_info)
    protocol = UniswapV3(generator.generate_state_at_block(time.start_block() - 1))
    numeraire = builder_state.builder_spot_oracle().numeraire
    historical_generator = HistoricalTxGenerator(f"{name}_historical_generator", name, time, generator)

    tokens_metadata = get_all_tokens()
    protocol_wrapper = UniswapV3Wrapper(
        name,
        protocol,
        numeraire,
        tokens_metadata,
    )
    return protocol_wrapper, historical_generator


def build_custom_state(info: dict) -> dict:
    return {
        "initial_state": {"custom_state": info},
        "random_generation_params": {},
        "protocol_type": UNISWAP_V3_ID,
    }


def build_simulation_state(
    time: SimulationTime, builder_state: MutBuilderSharedState, custom_state: dict
) -> UniswapV3Wrapper:
    Count.count += 1
    name = custom_state["pool_name"]
    custom_state_dict = build_custom_state(custom_state)

    spot = builder_state.builder_spot_oracle().build(time.clock_at(time.start_block() - 1))
    numeraire = spot.numeraire
    protocol = UniswapV3(
        uniswap_state_helper(
            Uniswapv3ProtocolInformation(
                name, custom_state_dict, Count.count, time.start_block(), time.start_time(), {}
            ).initial_state,
            spot,
        )
    )
    tokens_metadata = get_all_tokens()
    protocol_wrapper = UniswapV3Wrapper(name, protocol, numeraire, tokens_metadata)
    return protocol_wrapper


def build_random_generator(custom_state: dict, protocol: UniswapV3, time: SimulationTime) -> RandomTxGenerator:
    Count.count += 1
    rng = RandomGenerator()
    name = custom_state["pool_name"]
    univ3_generator = RandomUniv3Generator(Count.count, name, UNISWAP_V3_ID, custom_state, rng, {})
    observer = UniswapV3Observer(protocol)
    observer.set_environment(name, {})
    generator = RandomTxGenerator(f"{name}_random_generator", name, univ3_generator, observer, time)
    return generator
