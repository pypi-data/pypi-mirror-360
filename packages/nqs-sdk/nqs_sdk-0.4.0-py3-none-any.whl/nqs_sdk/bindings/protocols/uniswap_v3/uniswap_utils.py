import math
from decimal import Decimal


def price_to_tick(price: Decimal, decimals0: int, decimals1: int, tick_spacing: int = 1, lower: bool = True) -> int:
    # Compute tick as log base sqrt(1.0001) of sqrt_price
    ic = price.scaleb(decimals1 - decimals0).sqrt().ln() / Decimal("1.0001").sqrt().ln()
    if lower:
        tick = max(math.floor(round(ic) / tick_spacing) * tick_spacing, -887272)
    else:
        tick = min(math.ceil(round(ic) / tick_spacing) * tick_spacing, 887272)

    return tick


def tick_to_price(tick: int, decimals0: int, decimals1: int) -> Decimal:
    return (Decimal(1.0001) ** tick).scaleb(-(decimals1 - decimals0))


def price_to_sqrtp(p: Decimal) -> int:
    return int(p.sqrt() * Decimal("2") ** 96)


def calculate_max_amounts(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> Decimal:
    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    assert sqrt_price_lower < sqrt_price_upper

    if sqrt_price <= sqrt_price_lower:
        liquidity = amount0 / (1 / sqrt_price_lower - 1 / sqrt_price_upper)
    elif sqrt_price <= sqrt_price_upper:
        liquidity_0 = amount0 / (1 / sqrt_price - 1 / sqrt_price_upper)
        liquidity_1 = amount1 / (sqrt_price - sqrt_price_lower)
        liquidity = min(liquidity_0, liquidity_1)
    else:
        liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)

    return liquidity


def calculate_optimal_rebalancing(
    price_lower: Decimal, price: Decimal, price_upper: Decimal, amount0: Decimal, amount1: Decimal
) -> tuple[Decimal, Decimal]:
    sqrt_price_lower = price_lower.sqrt()
    sqrt_price = price.sqrt()
    sqrt_price_upper = price_upper.sqrt()

    x_unit = (sqrt_price_upper - sqrt_price) / (sqrt_price * sqrt_price_upper)
    y_unit = sqrt_price - sqrt_price_lower

    v_wallet = amount0 * price + amount1
    v_unit = x_unit * price + y_unit
    n_units = v_wallet / v_unit

    x_pos = n_units * x_unit
    y_pos = n_units * y_unit

    return x_pos, y_pos
