from typing import Any, List, Optional, Self, Tuple, cast

from nqs_pycore import Metrics, RefSharedState, SimulationClock, SimulationTime, TxRequest

from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk_extension.generator.random.random_transaction_generator import RandomTransactionGenerator
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer import ABCObserver
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction

if USE_LEGACY_QIS:
    from nqs_sdk_extension.shared_kernel.message_dispatcher import (
        ID,
        Message,
        MessageDispatcher,
        MessageListener,
        MessageProducer,
    )

if USE_LEGACY_QIS:

    class MockDispatcher(MessageDispatcher):
        message: Optional[Message] = None

        def register_producer(self, producer: MessageProducer, topic: str) -> ID:
            return producer.get_producer_id()

        def post(self, producer_id: ID, topic: str, message: Message) -> None:
            assert self.message is None
            self.message = message

        def direct_post(self, producer_id: ID, topic: str, message: Message) -> None:
            pass

        def register_listener(self, message_class: type, listener: MessageListener, topic: str = "DEFAULT") -> Self:
            return self

        def count_remaining_message_for_time_index(self, time_index: int, topic: str = "DEFAULT") -> int:
            return 0

        def start(self, **kwargs: Any) -> None:
            pass

        def start_pulling(self, low_time_index: int, high_time_index: int, topic: str = "DEFAULT") -> None:
            pass

        def take_message(self) -> Optional[Message]:
            msg = self.message
            self.message = None
            return msg


class RandomTxGenerator(TxGenerator):
    next_tx: Optional[ABCTransaction]

    def __init__(
        self,
        name: str,
        protocol_id: str,
        need_generator: RandomTransactionGenerator,
        observer: ABCObserver,
        time: SimulationTime,
    ) -> None:
        self.metrics: List[Any] = []
        self.name = name
        self.protocol_id = protocol_id
        if USE_LEGACY_QIS:
            self.dispatcher = MockDispatcher()
            need_generator.set_environment(protocol_id, self.dispatcher, observer)
            self.generator = need_generator
            self.poller = self.generator.produce_next_message(
                block_number_from=time.start_block(), block_number_to=time.stop_block()
            )
            self._poll_next_inner()

    def id(self) -> str:
        return self.name

    if USE_LEGACY_QIS:

        def _poll_next_inner(self) -> None:
            next(self.poller, None)
            message = self.dispatcher.take_message()
            self.next_tx = cast(Optional[ABCTransaction], message)

    def next(
        self, clock: SimulationClock, state: RefSharedState, metrics: Metrics
    ) -> Tuple[List[TxRequest], Optional[int]]:
        current_block = clock.current_block()
        txns = []

        while self.next_tx is not None and self.next_tx.block_number == current_block:
            txns.append(TxRequest.new_random(self.protocol_id, "Masao", self.next_tx))
            self._poll_next_inner()
        return (txns, getattr(self.next_tx, "block_number", None))

    def __str__(self) -> str:
        return f"generator: {self.generator}"
