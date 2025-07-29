from abc import ABC, abstractmethod

from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer import ABCObserver
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction

if USE_LEGACY_QIS:
    from legacy_qis.shared_kernel.message_dispatcher import MessageDispatcher, MessageProducer


class ABCSoloGenerator(MessageProducer if USE_LEGACY_QIS else object):  # type: ignore
    """
    A class representing a generator of states and transactions for a protocol.

    Attributes:
        id (int): the ID of the protocol
        name (str): the name of the protocol
    """

    def __init__(self, id: int, name: str) -> None:
        super().__init__(name)
        self.id = id
        self.name = name
        if USE_LEGACY_QIS:
            self._message_dispatcher: MessageDispatcher

    def set_seed(self, seed: int, use_antithetic_variates: bool) -> None:
        pass

    @abstractmethod
    def generate_state_at_block(self, block_number: int) -> ABCProtocolState:
        pass

    @abstractmethod
    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        pass

    @abstractmethod
    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        pass

    @abstractmethod
    def set_environment(self, env_protocol_id: str, env_observer: ABCObserver) -> None:
        """
        Set some environment properties / attributes
        """

    @abstractmethod
    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        """
        Takes two protocol states and compare them, typically logging a string.
        """


class ABCGenerator(ABC):
    """
    A class representing a generator of states and transactions for all the protocols.

    Attributes:
        protocols (dict): the list of protocols ID (int) and name (str) supported by the generator
    """

    def __init__(self, protocols: dict[int, str]):
        self.protocols = protocols

    @abstractmethod
    def generate_states_at_block(self, block_number: int) -> dict[int, ABCProtocolState]:
        pass

    @abstractmethod
    def generate_transactions_at_block(self, block_number: int) -> dict[int, list[ABCTransaction]]:
        pass

    @abstractmethod
    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int, protocol_id: str
    ) -> dict[int, list[ABCTransaction]]:
        pass
