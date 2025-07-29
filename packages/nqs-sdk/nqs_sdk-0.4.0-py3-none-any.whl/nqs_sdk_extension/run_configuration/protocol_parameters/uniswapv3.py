from dataclasses import dataclass

import numpy as np

from nqs_sdk_extension.generator.historical.dataquasar.uniswap_v3 import DTQUniswapV3Generator
from nqs_sdk_extension.run_configuration.protocol_parameters.protocol import SimulatedProtocolInformation
from nqs_sdk_extension.run_configuration.utils import TokenInfo
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.token_utils import wrap_token


@dataclass(kw_only=True)
class FakeStateUniv3(ABCProtocolState):
    id: int = 0
    token0: str
    token1: str
    symbol0: str
    symbol1: str
    decimals0: int
    decimals1: int
    fee_tier: int
    initial_balance0: int | None
    initial_balance1: int | None


class Uniswapv3ProtocolInformation(SimulatedProtocolInformation):
    default_tick_spacing = 1

    def __init__(
        self,
        protocol_name: str,
        protocol_info: dict,
        id: int,
        block_number_start: int,
        timestamp_start: int,
        token_info_dict: dict[str, TokenInfo],
    ) -> None:
        super().__init__(
            protocol_name=protocol_name,
            id=id,
            block_number_start=block_number_start,
            timestamp_start=timestamp_start,
            protocol_info=protocol_info,
            random_generation_params=protocol_info["random_generation_params"],
            token_info_dict=token_info_dict,
        )
        initial_state = protocol_info["initial_state"]
        if "custom_state" in initial_state.keys():
            self.initial_state = self.get_custom_state(custom_states=initial_state["custom_state"])
        elif "historical_state" in initial_state.keys():
            self.initial_state = self.get_historical_state(historical_states=initial_state["historical_state"])
        else:
            raise NotImplementedError("Only custom_state and historical_state are supported")

    def get_custom_state(self, custom_states: dict) -> ABCProtocolState:
        custom_states["symbol_token0"] = wrap_token(custom_states["symbol_token0"])
        custom_states["symbol_token1"] = wrap_token(custom_states["symbol_token1"])
        decimals0 = self.get_token_info(token=custom_states["symbol_token0"]).decimals
        decimals1 = self.get_token_info(token=custom_states["symbol_token1"]).decimals

        return uniswapv3_state_helper_full_range(
            id=self.id,
            name=self.protocol_name,
            block_number_start=self.block_number_start,
            custom_state=custom_states,
            decimals0=decimals0,
            decimals1=decimals1,
        )

    def get_historical_state(self, historical_states: dict) -> ABCProtocolState:
        token0 = wrap_token(historical_states.get("symbol_token0"))  # type: ignore
        token1 = wrap_token(historical_states.get("symbol_token1"))  # type: ignore
        address = str(historical_states.get("address"))
        historical_generator = DTQUniswapV3Generator(
            id=self.id, name=self.protocol_name, protocol_info={"address": address}
        )
        if historical_generator.symbol0 != token0:
            raise ValueError(
                f"The pool requested {token0}/{token1} with the specified fee tier does not exist. "
                f"Please simulate the inverse pair {token1}/{token0}"
            )
        pool_state = historical_generator.generate_state_at_block(self.block_number_start)

        self.set_token_info(token0, pool_state.decimals0, "0x" + token0)
        self.set_token_info(token1, pool_state.decimals1, "0x" + token1)
        return pool_state


def uniswapv3_state_helper_full_range(
    id: int, name: str, block_number_start: int, custom_state: dict, decimals0: int, decimals1: int
) -> FakeStateUniv3:
    """
    This function is used to create the initial state of a Uniswap v3 pool from the parameter file.
    The initial liquidity is set as full range.
    """
    initial_balance = custom_state["initial_balance"]
    initial_balance0, initial_balance1 = None, None

    if initial_balance["unit"] == "token0":
        initial_balance0 = initial_balance["amount"]
    elif initial_balance["unit"] == "token1":
        initial_balance1 = initial_balance["amount"]
    else:
        raise ValueError("The initial balance unit must be token0 or token1")

    return FakeStateUniv3(
        id=id,
        name=name,
        block_number=block_number_start,
        block_timestamp=0,
        symbol0=custom_state["symbol_token0"],
        symbol1=custom_state["symbol_token1"],
        token0="0x" + custom_state["symbol_token0"],
        token1="0x" + custom_state["symbol_token1"],
        decimals0=decimals0,
        decimals1=decimals1,
        fee_tier=int(custom_state["fee_tier"] * 1_000_000),
        initial_balance0=initial_balance0,
        initial_balance1=initial_balance1,
    )


def uniswapv3_price_helper(price: float) -> int:
    return int(np.sqrt(price) * (2**96))
