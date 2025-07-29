from nqs_sdk_extension.generator.historical.dataquasar.compound_v2 import DTQCompoundv2Generator
from nqs_sdk_extension.run_configuration.protocol_parameters.protocol import SimulatedProtocolInformation
from nqs_sdk_extension.run_configuration.utils import CTOKEN_DECIMALS, DEFAULT_TOKEN_DECIMALS, CTokenInfo, TokenInfo
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.state.compoundv2 import (
    BorrowSnapshot,
    StateCompoundMarket,
    StateComptroller,
    StateInterestRateModel,
)
from nqs_sdk_extension.token_utils import wrap_token


class Compoundv2ProtocolInformation(SimulatedProtocolInformation):
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
            token_info_dict=token_info_dict,
        )
        self.comptroller_state: StateComptroller
        self.market_id = -1
        initial_state = protocol_info["initial_state"]
        if "custom_state" in initial_state.keys():
            initial_state = self.get_custom_state(custom_states=initial_state["custom_state"])
        elif "historical_state" in initial_state.keys():
            initial_state = self.get_historical_state(historical_states=initial_state["historical_state"])
        else:
            raise NotImplementedError("Only custom_state and historical_state are supported")

        self.initial_state = initial_state
        for market_params in protocol_info["random_generation_params"]["markets"]:
            self.random_generation_params[wrap_token(market_params["market"])] = market_params

    def set_ctoken_info(self, ctoken: str, underlying_token: str, address: str, underlying_address: str) -> None:
        if ctoken in self.token_info_dict:
            return

        self.token_info_dict[ctoken] = CTokenInfo(
            underlying_symbol=underlying_token,
            decimals=CTOKEN_DECIMALS,
            name=ctoken + "coin",
            address=address,
            underlying_address=underlying_address,
            comptroller_id=self.protocol_name,
        )

    def get_custom_state(self, custom_states: dict) -> ABCProtocolState:
        market_states = {}
        for custom_market_state in custom_states["markets"]:
            custom_market_state["market"] = wrap_token(custom_market_state["market"])
            underlying_symbol = custom_market_state["market"]
            interest_rate_model = compoundv2_interest_rate_model_helper(custom_market_state, 10**DEFAULT_TOKEN_DECIMALS)
            underlying_decimals = self.get_token_info(underlying_symbol).decimals
            market_symbol = "c" + underlying_symbol
            market_state = compoundv2_state_helper(
                custom_market_state,
                self.market_id,
                market_symbol,
                self.block_number_start,
                interest_rate_model,
                underlying_decimals,
            )
            market_states[market_symbol] = market_state
            self.set_ctoken_info(
                ctoken=market_symbol,
                underlying_token=underlying_symbol,
                address="0x" + market_symbol,
                underlying_address="0x" + underlying_symbol,
            )
            self.additional_parameters[underlying_symbol] = {"ctoken": market_symbol}
            self.market_id -= 1

        return StateComptroller(
            id=self.id,
            name=self.protocol_name,
            block_number=self.block_number_start,
            block_timestamp=0,
            close_factor_mantissa=int(
                custom_states["comptroller"]["close_factor_mantissa"] * 10**DEFAULT_TOKEN_DECIMALS
            ),
            liquidation_incentive_mantissa=int(
                custom_states["comptroller"]["liquidation_incentive_mantissa"] * 10**DEFAULT_TOKEN_DECIMALS
            ),
            max_assets=custom_states["comptroller"].get("max_assets", 20),
            market_states=market_states,
        )

    def get_historical_state(self, historical_states: dict) -> ABCProtocolState:
        markets = historical_states.get("markets", [])
        if len(markets) == 0:
            raise ValueError("No markets have been specified")
        ctokens = ["c" + wrap_token(x["market"]) for x in markets]
        historical_generator = DTQCompoundv2Generator(
            id=self.id, name="DTQCompoundv2Generator", protocol_info={"markets": ctokens}
        )

        comptroller_state = historical_generator.generate_state_at_block(self.block_number_start, self.id)

        for market_state in comptroller_state.market_states.values():
            self.set_ctoken_info(
                ctoken=market_state.symbol,
                underlying_token=market_state.underlying,
                address=market_state.address,
                underlying_address=market_state.underlying_address,
            )
            self.additional_parameters[market_state.underlying] = {
                "ctoken": market_state.symbol,
                "underlying_decimals": market_state.underlying_decimals,
            }
            self.set_token_info(
                market_state.underlying, market_state.underlying_decimals, market_state.underlying_address
            )

        return comptroller_state


def compoundv2_interest_rate_model_helper(custom_state: dict, default_multiplicator: int) -> StateInterestRateModel:
    return StateInterestRateModel(
        multiplier_per_block=int(custom_state["interest_rate_model"]["multiplier_per_block"] * default_multiplicator),
        base_rate_per_block=int(custom_state["interest_rate_model"]["base_rate_per_block"] * default_multiplicator),
        jump_multiplier_per_block=int(
            custom_state["interest_rate_model"]["jump_multiplier_per_block"] * default_multiplicator
        ),
        kink=int(custom_state["interest_rate_model"]["kink"] * default_multiplicator),
    )


def compoundv2_state_helper(
    custom_state: dict,
    market_id: int,
    market_symbol: str,
    block_number_start: int,
    interest_rate_model: StateInterestRateModel,
    underlying_decimals: int,
) -> StateCompoundMarket:
    return StateCompoundMarket(
        id=market_id,
        name="Compound market " + market_symbol,
        block_number=block_number_start,
        block_timestamp=0,
        symbol=market_symbol,
        address="0x" + market_symbol,
        underlying=custom_state["market"],
        underlying_address="0x" + custom_state["market"],
        underlying_decimals=underlying_decimals,
        interest_rate_model=interest_rate_model,
        decimals=CTOKEN_DECIMALS,
        initial_exchange_rate_mantissa=int(
            custom_state.get("initial_exchange_rate_mantissa", 0.02)
            * 10 ** (18 - CTOKEN_DECIMALS + underlying_decimals)
        ),
        accrual_block_number=block_number_start,
        reserve_factor_mantissa=int(custom_state["reserve_factor_mantissa"] * 10**DEFAULT_TOKEN_DECIMALS),
        borrow_index=int(custom_state.get("borrow_index", 1_000_000_000_000_000_000)),
        total_borrows=int(custom_state["total_borrows"] * 10**underlying_decimals),
        total_supply=int(custom_state["total_supply"] * 10**CTOKEN_DECIMALS),
        total_reserves=int(custom_state["total_reserves"] * 10**underlying_decimals),
        collateral_factor=int(custom_state["collateral_factor"] * 10**DEFAULT_TOKEN_DECIMALS),
        borrow_cap=int(custom_state.get("borrow_cap", 0) * 10**underlying_decimals),
        account_borrows={
            wallet: BorrowSnapshot(
                principal=custom_state["account_borrows"][wallet]["principal"] * 10**underlying_decimals,
                interest_index=custom_state["account_borrows"][wallet]["interest_index"],
            )
            for wallet in custom_state.get("account_borrows", {}).keys()
        },
        total_cash=custom_state["total_cash"] * 10**underlying_decimals,
    )
