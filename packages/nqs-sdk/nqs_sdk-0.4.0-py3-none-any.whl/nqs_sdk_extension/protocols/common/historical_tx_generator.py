from typing import List, Optional, Tuple

from nqs_pycore import Metrics, RefSharedState, SimulationClock, SimulationTime, TxRequest

from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk_extension.generator.abc_generator import ABCSoloGenerator


class HistoricalTxGenerator(TxGenerator):
    def __init__(
        self,
        name: str,
        protocol_id: str,
        time: SimulationTime,
        need_generator: ABCSoloGenerator,
    ) -> None:
        self.name = name
        self.protocol_id = protocol_id
        self.next_tx_pos = 0
        self.metrics = List
        self.transactions = []

        block_number_to = time.stop_block() or 2**63
        block_number_batch_from = time.start_block()
        while block_number_batch_from < block_number_to:
            # using a 50000 batch size, following rust implementation so they
            # can share the quantlib cache.
            block_number_batch_to = min(block_number_to, block_number_batch_from + 50000)
            # Assumption: retrieved transactions are already ordered by increasing block number
            self.transactions.extend(
                need_generator.generate_transactions_between_blocks(block_number_batch_from, block_number_batch_to)
            )
            block_number_batch_from = block_number_batch_to

    def id(self) -> str:
        return self.name

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        current_block = clock.current_block()
        txns = []

        next_block_number = None
        while self.next_tx_pos < len(self.transactions):
            tx = self.transactions[self.next_tx_pos]
            tx_block_number = tx.block_number
            if tx_block_number == current_block:
                txns.append(TxRequest.new_random(self.protocol_id, "Masao", tx))
            elif tx_block_number > current_block:
                next_block_number = tx_block_number
                break
            self.next_tx_pos += 1

        return (txns, next_block_number)

    def __str__(self) -> str:
        return f"generator: {self.id()}"
