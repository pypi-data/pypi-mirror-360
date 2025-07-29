import logging
from dataclasses import dataclass, field

from nqs_sdk_extension.observer.protocol.amm_utils import uniswap_v3_il  # type: ignore
from nqs_sdk_extension.observer.protocol.buffer import TimeSeriesBuffer


# TODO: one could make a generic class for token metrics with a common interface
# Note: store data in user-friendly units (i.e. float, not int)
@dataclass(kw_only=True)
class TokenMetricsUniv3:
    token_id: str
    tick_lower: int
    tick_upper: int
    price_lower: float
    price_upper: float
    # last state
    block_number: int
    liquidity: int
    initial_amount0: float
    initial_amount1: float
    factor_liquidity: float
    price: float
    market_spot: float
    # state history: used to compute IL and LVR
    state_history: list[tuple[int, int, float, float]] = field(init=False)  # use named tuple?
    # metrics values updated from initial state to last state
    # - FEES COLLECTED
    fee_collected0: int = 0
    fee_collected1: int = 0
    # - LVR
    lvr: float = 0.0
    lvr_block_number_last: int = field(init=False)
    # - IL
    il_open_positions: list[tuple[int, float, int]] = field(init=False)  # (block_number, price, liquidity)
    # - PL
    abs_pl: int = 0
    abs_pl_num: int = 0  # in numéraire units
    # keep track of closed positions (not used for now - for debugging purposes)
    closed_positions: list[tuple[int, int, float, float]] = field(
        init=False
    )  # (block_number_open, block_number_closed, liquidity, pl)

    def __post_init__(self) -> None:
        self.state_history = []
        self.state_history.append((self.block_number, self.liquidity, self.price, self.market_spot))
        self.lvr_block_number_last = self.block_number
        self.il_open_positions = []
        self.il_open_positions.append((self.block_number, self.price, self.liquidity))
        self.closed_positions = []

    def update_from_collect_event(self, amount0: int, amount1: int) -> None:
        self.fee_collected0 += amount0
        self.fee_collected1 += amount1
        # no need to update state history

    def update_from_update_event(self, block_number: int, delta_amount: int, price: float, market_spot: float) -> None:
        self.block_number = block_number
        if self.liquidity == 0:
            assert (
                self.initial_amount0 == 0 and self.initial_amount1 == 0
            ), "Initial amounts should be zero if liquidity is zero"
        else:
            self.initial_amount0 *= 1 + delta_amount / self.liquidity
            self.initial_amount1 *= 1 + delta_amount / self.liquidity
        self.liquidity += delta_amount
        self.price = price
        self.market_spot = market_spot
        # update state history
        self.state_history.append((self.block_number, self.liquidity, self.price, self.market_spot))
        # update open positions
        if delta_amount > 0:
            self.il_open_positions.append((self.block_number, self.price, delta_amount))
        # update closed positions
        while delta_amount < 0:
            # FILO
            block_open, price_open, liquidity_open = self.il_open_positions.pop()
            liquidity_to_close = min(-delta_amount, liquidity_open)
            delta_amount += liquidity_to_close
            _, abs_il, _ = uniswap_v3_il(
                self.price_lower, self.price_upper, price_open, price, liquidity_to_close * self.factor_liquidity
            )
            # update PL
            self.abs_pl += abs_il
            self.abs_pl_num += abs_il * market_spot
            # update closed positions
            self.closed_positions.append((block_open, block_number, liquidity_to_close, abs_il))
            # update open positions if needed
            liquidity_remaining = liquidity_open - liquidity_to_close
            if liquidity_remaining > 0:
                self.il_open_positions.append((block_open, price_open, liquidity_remaining))

    # Note: may be slow if there are many state updates
    def get_liquidity_at_block(self, block_number: int) -> int:
        # find the last state before block_number
        for i, (block, _, _, _) in enumerate(self.state_history):
            if block > block_number:
                return self.state_history[i - 1][1]
        return self.liquidity

    # TODO: use an interface for the buffer
    def update_lvr_from_buffer(self, buffer: TimeSeriesBuffer) -> None:
        # check if the buffer is non-empty
        if len(buffer.block_vec) == 0:
            logging.warning("Buffer is empty, cannot compute LVR")
            return None
        # check that we have enough buffer history
        if buffer.block_vec[0] > self.lvr_block_number_last:
            raise ValueError("Not enough buffer history to compute LVR")
            # find index of last block
        index = 0
        for i, block_number in enumerate(buffer.block_vec):
            if block_number > self.lvr_block_number_last:
                index = i
                break
        if index == 0:
            return None  # no new data
        # compute LVR increment
        lvr = 0.0
        for i in range(index, len(buffer.block_vec)):
            block_prev = buffer.block_vec[i - 1]
            if block_prev < self.lvr_block_number_last:
                continue  # seems redundant
            price_prev = buffer.price_vec[i - 1]
            liquidity_prev = self.get_liquidity_at_block(block_prev) * self.factor_liquidity
            # check that the price is within bounds
            if (price_prev > self.price_lower) and (price_prev < self.price_upper):
                dt = buffer.dt_vec[i]
                rvol_prev = buffer.rvol_vec[i - 1]
                # LVR formula
                lvr += 0.25 * liquidity_prev * rvol_prev**2 * price_prev**0.5 * dt
        # update token metrics
        self.lvr_block_number_last = buffer.last_block_number  # type: ignore
        if lvr < 0:
            raise ValueError("LVR cannot be negative")
        self.lvr += lvr
