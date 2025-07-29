from dataclasses import dataclass

from nqs_sdk_extension.state import ABCProtocolState


@dataclass
class BorrowSnapshot:
    principal: int
    interest_index: int


@dataclass
class StateInterestRateModel:
    """
    A class representing the snapshot of a Compound V2 interest rate model
    """

    multiplier_per_block: int
    base_rate_per_block: int
    jump_multiplier_per_block: int
    kink: int
    base: int = 10**18
    blocks_per_year: int = 2102400


@dataclass
class StateCompoundMarket(ABCProtocolState):
    """
    A class representing the snapshot of a Compound V2 cToken
    """

    name: str
    symbol: str
    address: str
    underlying: str
    underlying_address: str
    interest_rate_model: StateInterestRateModel
    decimals: int
    underlying_decimals: int
    initial_exchange_rate_mantissa: int
    accrual_block_number: int
    reserve_factor_mantissa: int
    borrow_index: int
    total_borrows: int
    total_supply: int
    total_reserves: int
    collateral_factor: int
    borrow_cap: int
    account_borrows: dict[str, BorrowSnapshot]
    total_cash: int  # this is the amount of underlying owned by the cToken contract
    protocol_seize_share_mantissa: int = 28 * 10**15
    borrow_rate_max_mantissa: int = 5 * 10**12
    reserve_factor_max_mantissa: int = 10**18


@dataclass
class StateComptroller(ABCProtocolState):
    """
    A class representing the snapshot of the Compound V2 Comptroller
    """

    close_factor_mantissa: int
    liquidation_incentive_mantissa: int
    max_assets: int
    market_states: dict[str, StateCompoundMarket]
