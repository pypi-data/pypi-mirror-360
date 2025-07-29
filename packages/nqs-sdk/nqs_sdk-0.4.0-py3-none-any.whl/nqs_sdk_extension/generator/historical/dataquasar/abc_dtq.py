import logging
from abc import abstractmethod
from collections import Counter
from typing import Any, List, Tuple

from nqs_sdk.utils.pickable_generator import PickableGenerator, StatefulGenerator
from nqs_sdk_extension.constants import BLOCKS_BATCH_SIZE
from nqs_sdk_extension.generator.abc_generator import ABCSoloGenerator
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer import ABCObserver
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction

if USE_LEGACY_QIS:
    from legacy_qis.shared_kernel.message_dispatcher import MessageDispatcher


class DTQSoloGenerator(ABCSoloGenerator):
    """
    A class to generate protocol states and transactions using DataQuasar
    """

    def __init__(self, id: int, name: str):
        super().__init__(id, name)

    if USE_LEGACY_QIS:

        def set_environment(  # type: ignore[override]
            self, env_protocol_id: str, env_message_dispatcher: MessageDispatcher, env_observer: ABCObserver
        ) -> None:
            """
            Sets the protocol_id that maps the generator to a protocol, in the environment.
            """
            self._protocol_id = env_protocol_id
            self._message_dispatcher = env_message_dispatcher
            self._message_dispatcher.register_producer(self, "TRANSACTIONS")

    def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
        block_number_from = kwargs.get("block_number_from", -1)
        block_number_to = kwargs.get("block_number_to", -1)

        def update(
            state: Tuple[DTQSoloGenerator, List[ABCTransaction], int, int],
        ) -> Tuple[Tuple[DTQSoloGenerator, List[ABCTransaction], int, int], None]:
            object, current_transactions, block_number_from, block_number_to = state

            # Keep fetching batches until we have transactions or reach the end
            while not current_transactions:
                if block_number_from >= block_number_to:
                    raise StopIteration()

                block_number_to_tmp = min(block_number_from + BLOCKS_BATCH_SIZE, block_number_to)

                # Generate transactions between blocks
                transactions = self.generate_transactions_between_blocks(
                    block_number_from=block_number_from, block_number_to=block_number_to_tmp
                )

                # Move block range forward
                block_number_from = block_number_to_tmp

                # If transactions found, process and prepare
                if transactions:
                    # Reorder transactions
                    transactions = sorted(transactions, key=lambda obj: obj.block_number)

                    # Log category counts
                    category_counts = Counter(txn.action_type for txn in transactions)
                    for category, count in category_counts.items():
                        logging.debug(f"Category: {category}, Count: {count}")

                    current_transactions = transactions
                    break

            # Pop and dispatch the next transaction
            assert len(current_transactions) > 0  # due to previous 'while not current_transactions:'
            tx = current_transactions.pop(0)
            self._message_dispatcher.post(producer_id=self.get_producer_id(), topic="TRANSACTIONS", message=tx)  # type: ignore
            return (object, current_transactions, block_number_from, block_number_to), None

        return StatefulGenerator((self, [], block_number_from, block_number_to), update)

    @abstractmethod
    def generate_state_at_block(self, block_number: int) -> ABCProtocolState:
        pass
