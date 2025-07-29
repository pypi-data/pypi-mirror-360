# type: ignore

import numpy as np

from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.state import StateUniv3


def _price_range(price: float, pct: float) -> tuple[float, float]:
    return price * (1 - pct / 100), price * (1 + pct / 100)


def _univ3_prepare_liquidity_position(
    state: StateUniv3, min_price: float, max_price: float, inverse_price: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    ticks = state.ticks
    # Compute the prices
    decimals0 = state.decimals0
    decimals1 = state.decimals1
    prices = np.array([TickMath.tick_to_price(tick.tick_idx, decimals0, decimals1) for tick in ticks])
    # Compute the liquidity distribution
    liquidity_dist = np.cumsum([t.liquidity_net for t in ticks])[:-1]
    # Select the interval of ticks
    indices = (prices > min_price) & (prices < max_price)
    indices = np.where(indices)[0]
    prices = prices[indices]
    liquidity_dist = liquidity_dist[indices]
    if inverse_price:
        prices = 1 / prices
        prices = prices[::-1]
        liquidity_dist = liquidity_dist[::-1]
    return prices, liquidity_dist


def univ3_plotly_liquidity_position(state: StateUniv3, range_pct: int | None, inverse_price: bool = False) -> None:
    import plotly.graph_objects as go

    price = TickMath.sqrt_price_x96_to_price(state.sqrt_price_x96, state.decimals0, state.decimals1)
    min_price, max_price = _price_range(price, range_pct)
    prices, liquidity_dist = _univ3_prepare_liquidity_position(state, min_price, max_price, inverse_price)
    # Create bar plot with custom bin boundaries
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=prices[:-1],
            y=liquidity_dist,
            width=np.diff(prices),
            marker_line_width=0,
            name=f"{state.name}-{state.block_number}",
        )
    )
    # Set y-axis to logarithmic scale
    # fig.update_yaxes(type='log')
    # Add axis names
    fig.update_xaxes(title_text="Price")
    fig.update_yaxes(title_text="Liquidity Distribution")
    fig.show()
    return None


def univ3_plotly_compare_liquidity_position(
    state1: StateUniv3, state2: StateUniv3, range_pct: int, inverse_price: bool = False
):
    import plotly.graph_objects as go

    price = TickMath.sqrt_price_x96_to_price(state1.sqrt_price_x96, state1.decimals0, state1.decimals1)
    min_price, max_price = _price_range(price, range_pct)
    prices1, liquidity_dist1 = _univ3_prepare_liquidity_position(state1, min_price, max_price, inverse_price)
    prices2, liquidity_dist2 = _univ3_prepare_liquidity_position(state2, min_price, max_price, inverse_price)
    # Create bar plot with custom bin boundaries
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=prices1[:-1],
            y=liquidity_dist1,
            width=np.diff(prices1),
            marker_line_width=0,
            name=f"{state1.name}-{state1.block_number}",
        )
    )
    fig.add_trace(
        go.Bar(
            x=prices2[:-1],
            y=liquidity_dist2,
            width=np.diff(prices2),
            marker_line_width=0,
            opacity=0.6,
            name=f"{state2.name}-{state2.block_number}",
        )
    )
    # Add axis names
    fig.update_xaxes(title_text="Price")
    fig.update_yaxes(title_text="Liquidity Distribution")
    fig.show()
    return None
