import logging
from dataclasses import dataclass, field

from nqs_sdk_extension.constants import BUFFER_BLOCK_SAMPLING, BUFFER_LAMBDA_COEF

FACTOR_SECONDS_TO_YEAR = 1.0 / (60 * 60 * 24 * 365.25)  # map seconds diff to year fraction


# TODO: create an interface for the buffer so that we do not access the variables directly
@dataclass(kw_only=True)
class TimeSeriesBuffer:
    block_sampling: int = BUFFER_BLOCK_SAMPLING  # block sampling frequency, approx 5 minutes
    lambda_coef: float = BUFFER_LAMBDA_COEF  # decay factor for EWMA from RM97
    last_block_number: int | None = None
    flush_from_block_number: int | None = None
    last_block_timestamp: int | None = None
    block_vec: list[int] = field(default_factory=list)
    price_vec: list[float] = field(default_factory=list)
    rets_vec: list[float] = field(default_factory=list)
    rvol_vec: list[float] = field(default_factory=list)
    dt_vec: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.block_vec = []
        self.price_vec = []
        self.rets_vec = []
        self.rvol_vec = []
        self.dt_vec = []
        self.logger = logging.getLogger(__name__)

    def updatable(self, block_number: int) -> bool:
        return (
            # First event
            (self.last_block_number is None)
            # Enough time has passed
            or (block_number - self.last_block_number >= self.block_sampling)
            # Same block
            or (block_number == self.last_block_number and len(self.dt_vec) >= 2)
        )

    def update_from_swap_event(self, price: float, block_number: int, block_timestamp: int) -> None:
        self.logger.debug(f"block number: {block_number}")
        if not self.updatable(block_number):
            raise ValueError
        if self.last_block_timestamp is None:
            # first event is initialized with zeros
            ret = ret_scaled = dt = rvol = 0.0
        elif block_number != self.last_block_number:
            # delta time
            dt = (block_timestamp - self.last_block_timestamp) * FACTOR_SECONDS_TO_YEAR
            # log-return
            ret = (price - self.price_vec[-1]) / self.price_vec[-1]
            # scale return by square root of dt
            ret_scaled = ret / (dt**0.5)
            # realized volatility approximation RM97
            rvol = self.lambda_coef * self.rvol_vec[-1] + (1 - self.lambda_coef) * ret_scaled**2
        elif block_number == self.last_block_number:
            # Pop the last elements as they will be replaced
            dt = self.dt_vec.pop(-1)
            # if the block number is the same, we do not update dt
            last_price = self.price_vec.pop(-1)
            last_ret = self.rets_vec.pop(-1)
            self.rvol_vec.pop(-1)
            self.block_vec.pop(-1)

            # Intra block return
            new_ret = (price - last_price) / last_price
            # Compounded return since last price update
            ret = (1 + new_ret) * (1 + last_ret) - 1
            ret_scaled = ret / (dt**0.5)
            rvol = self.lambda_coef * self.rvol_vec[-1] + (1 - self.lambda_coef) * ret_scaled**2

        # store values in the buffer
        self.block_vec.append(block_number)
        self.price_vec.append(price)
        self.dt_vec.append(dt)
        self.rets_vec.append(ret)
        self.rvol_vec.append(rvol)
        self.last_block_number = block_number
        self.last_block_timestamp = block_timestamp

    # XXX: only this method is used
    def flush_to_last_observation(self) -> None:
        self.flush_from_block_number = self.last_block_number
        self.flush()

    # TODO: amend the above method and delete this one
    def flush(self) -> None:
        flush_from_block_number = self.flush_from_block_number
        if flush_from_block_number is None:
            return None
        index = len(self.block_vec) - 1
        for i, block_number in enumerate(self.block_vec):
            if block_number == flush_from_block_number:
                index = i
                break
            if block_number > flush_from_block_number:
                index = max(0, i - 2)  # make sure we do not remove the last two blocks
                break
        self.block_vec = self.block_vec[index:]
        self.price_vec = self.price_vec[index:]
        self.rets_vec = self.rets_vec[index:]
        self.rvol_vec = self.rvol_vec[index:]
        self.dt_vec = self.dt_vec[index:]
