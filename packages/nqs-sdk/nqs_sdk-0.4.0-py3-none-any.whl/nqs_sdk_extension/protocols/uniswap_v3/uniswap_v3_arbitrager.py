import logging
from typing import List, Optional, Tuple

from nqs_pycore import Metrics, RefSharedState, SimulationClock, SimulationTime, TxRequest

from nqs_sdk.interfaces.tx_generator import TxGenerator


class ArbitrageTransaction: ...


class UniswapV3Arbitrager(TxGenerator):
    def __init__(self, time: SimulationTime, ids: List[str], interval: int):
        self.start_block = time.start_block()
        self.ids = ids
        self.interval = interval

    def id(self) -> str:
        return "uniswap_v3_arbitrager"

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        offset = (clock.current_block() - self.start_block) % self.interval
        if offset != 0:
            logging.debug(clock.current_block() + self.interval - offset)
            # request run at next arbitrage point even if no other transactions run
            return [], clock.current_block() + self.interval - offset
        # None for the next block required guarantees that it will run on the next block where transactions happen,
        # essentially skipping empty blocks as no arbitrage is needed if nothing happens
        return [self._build_arbitrage(protocol) for protocol in self.ids], None

    def _build_arbitrage(self, protocol_id: str) -> TxRequest:
        tx = TxRequest.new_random(protocol_id, self.id(), ArbitrageTransaction())
        tx.order = 1000000
        return tx
