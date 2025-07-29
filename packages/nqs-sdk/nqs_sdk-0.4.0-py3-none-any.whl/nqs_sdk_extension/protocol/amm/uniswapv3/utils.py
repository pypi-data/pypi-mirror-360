from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple

# ------------------------------------------------------------
# Data structures used by the protocol Swap methods
# ------------------------------------------------------------

"""
@dataclass(kw_only=True)
class SwapCache:
    # the protocol fee for the input token
    feeProtocol: int
    # liquidity at the beginning of the swap
    liquidity_start: int
    # the timestamp of the current block
    blockTimestamp: int
    # the current value of the tick accumulator, computed only if we cross an initialized tick
    tickCumulative: int
    # the current value of seconds per liquidity accumulator, computed only if we cross an initialized tick
    secondsPerLiquidityCumulativeX128: int
    # whether we've computed and cached the above two accumulators
    computedLatestObservation: bool
"""


@dataclass(kw_only=True)
class SwapState:
    # the amount remaining to be swapped in/out of the input/output asset
    amount_specified_remaining: int
    # the amount already swapped out/in of the output/input asset
    amount_calculated: int
    # current sqrt(price)
    sqrt_price_x96: int
    # the tick associated with the current price
    tick: int
    # the global fee growth of the input token
    fee_growth_global_x128: int
    # amount of input token paid as protocol fee
    protocol_fee: int
    # the current liquidity in range
    liquidity: int


@dataclass(kw_only=True)
class StepComputations:
    # the price at the beginning of the step
    sqrt_price_start_x96: int | None = None
    # the next tick to swap to from the current tick in the swap direction
    tick_next: int | None = None
    # whether tick_next is initialized or not
    initialized: bool | None = None
    # sqrt(price) for the next tick (1/0)
    sqrt_price_next_x96: int | None = None
    # how much is being swapped in this step
    amount_in: int | None = None
    # how much is being swapped out
    amount_out: int | None = None
    # how much fee is being paid in
    fee_amount: int | None = None


def calculate_amounts(
    sqrt_price_lower: float,
    sqrt_price: float,
    sqrt_price_upper: float,
    user_input_amount0: int | None,
    user_input_amount1: int | None,
    user_input_amount: int | None,
    decimals0: int,
    decimals1: int,
) -> Tuple[float | int | None, float | int | None, float | int | None]:
    flag0 = user_input_amount0 is not None
    flag1 = user_input_amount1 is not None
    flag = user_input_amount is not None
    amount0_tmp: float | int | None
    amount1_tmp: float | int | None
    amount_tmp: float | int | None

    if flag and not flag0 and not flag1:
        amount_float = float(Decimal(str(user_input_amount)).scaleb(-((decimals0 + decimals1) // 2)))
        amount0_tmp, amount1_tmp = lp_from_liquidity_to_amount0_amount1(
            sqrt_price, sqrt_price_lower, sqrt_price_upper, amount_float
        )
        amount_tmp = user_input_amount

    elif not flag and flag0 and not flag1:
        if user_input_amount0 is None:
            raise ValueError("Error : amount0 is None")  # to handle mypy, not expected to happen

        amount0_float = float(Decimal(str(user_input_amount0)).scaleb(-decimals0))
        amount_tmp, amount1_tmp = lp_from_amount0_to_liquidity_amount1(
            sqrt_price, sqrt_price_lower, sqrt_price_upper, amount0_float
        )
        amount0_tmp = user_input_amount0

    elif not flag and flag1 and not flag0:
        if user_input_amount1 is None:
            raise ValueError("Error : amount1 is None")  # to handle mypy, not expected to happen

        amount1_float = float(Decimal(str(user_input_amount1)).scaleb(-decimals1))
        amount_tmp, amount0_tmp = lp_from_amount1_to_liquidity_amount0(
            sqrt_price, sqrt_price_lower, sqrt_price_upper, amount1_float
        )
        amount1_tmp = user_input_amount1

    else:
        raise ValueError("Error : Got more than one of amount, amount0, amount1")  # Not expected to happen

    if amount_tmp is None:
        return None, None, None

    amount, amount0, amount1 = scale_decimals(
        amount0_tmp, amount1_tmp, amount_tmp, decimals0, decimals1, flag, flag0, flag1
    )

    return amount, amount0, amount1


def scale_decimals(
    amount0: float | int | None,
    amount1: float | int | None,
    amount: float | int | None,
    decimals0: int,
    decimals1: int,
    flag: bool,
    flag0: bool,
    flag1: bool,
) -> Tuple[float | int | None, float | int | None, float | int | None]:
    if flag and not flag0 and not flag1:
        if amount is None:
            raise ValueError("Error : amount is None")  # for mypy, not expected to happen
        amount0 = int(amount0 * (10**decimals0))
        amount1 = int(amount1 * (10**decimals1))
        amount = int(amount)
    elif not flag and flag0 and not flag1:
        if amount0 is None:
            raise ValueError("Error : amount0 is None")  # for mypy, not expected to happen
        amount0 = int(amount0)
        amount1 = int(amount1 * (10**decimals1))
        amount = int(amount * (10 ** ((decimals0 + decimals1) // 2)))
    elif not flag and not flag0 and flag1:
        if amount1 is None:
            raise ValueError("Error : amount1 is None")  # for mypy, not expected to happen

        amount0 = int(amount0 * (10**decimals0))
        amount1 = int(amount1)
        amount = int(amount * (10 ** ((decimals0 + decimals1) // 2)))

    return amount, amount0, amount1


def lp_from_liquidity_to_amount0_amount1(
    sqrt_price: float, sqrt_price_lower: float, sqrt_price_upper: float, liquidity: float
) -> tuple[float | None, float | None]:
    # three different cases
    if sqrt_price <= sqrt_price_lower:
        amount0 = liquidity / sqrt_price_lower - liquidity / sqrt_price_upper
        amount1 = 0.0
    elif sqrt_price >= sqrt_price_upper:
        amount0 = 0.0
        amount1 = liquidity * sqrt_price_upper - liquidity * sqrt_price_lower
    else:
        amount0 = liquidity / sqrt_price - liquidity / sqrt_price_upper
        amount1 = liquidity * sqrt_price - liquidity * sqrt_price_lower
    return amount0, amount1


def lp_from_amount0_to_liquidity_amount1(
    sqrt_price: float, sqrt_price_lower: float, sqrt_price_upper: float, amount0: float
) -> tuple[float | None, float | None]:
    # three different cases
    if sqrt_price <= sqrt_price_lower:
        liquidity = amount0 / (1 / sqrt_price_lower - 1 / sqrt_price_upper)
        amount1 = 0.0
    elif sqrt_price >= sqrt_price_upper:
        return None, None
    else:
        liquidity = amount0 / (1 / sqrt_price - 1 / sqrt_price_upper)
        amount1 = liquidity * sqrt_price - liquidity * sqrt_price_lower
    return liquidity, amount1


def lp_from_amount1_to_liquidity_amount0(
    sqrt_price: float, sqrt_price_lower: float, sqrt_price_upper: float, amount1: float
) -> tuple[float | None, float | None]:
    if sqrt_price <= sqrt_price_lower:
        return None, None
    elif sqrt_price >= sqrt_price_upper:
        amount0 = 0.0
        liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)
    else:
        liquidity = amount1 / (sqrt_price - sqrt_price_lower)
        amount0 = liquidity / sqrt_price - liquidity / sqrt_price_upper
    return liquidity, amount0
