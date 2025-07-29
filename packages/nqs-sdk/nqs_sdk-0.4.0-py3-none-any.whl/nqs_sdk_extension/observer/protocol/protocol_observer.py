from abc import abstractmethod
from typing import Optional, Sequence

from nqs_pycore import Wallet

from nqs_sdk_extension.agent.agent_action import CustomVariable
from nqs_sdk_extension.observer.abc_observer import ABCObserver, SingleObservable
from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction


class ProtocolObserver(ABCObserver):
    def __init__(self, protocol: Optional[ABCProtocol] = None) -> None:
        super().__init__()

    @abstractmethod
    def exists_arbitrage_opportunity(self, block_number: int, block_timestamp: int) -> bool:
        pass

    @abstractmethod
    def create_arbitrage_transactions(
        self, block_number: int, block_timestamp: int, arbitrageur_wallet: Wallet
    ) -> Sequence[ABCTransaction]:
        pass

    @abstractmethod
    def agents_id_to_update(self) -> list[str]:
        pass

    @abstractmethod
    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        pass

    def flush_buffer(self) -> None:
        pass

    def get_custom_variable(self, variable_name: str) -> CustomVariable:
        raise NotImplementedError
