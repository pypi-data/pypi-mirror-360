from typing import Dict, Optional, Sequence

from nqs_pycore import Wallet

from nqs_sdk_extension.observer import ABCObserver, SingleObservable
from nqs_sdk_extension.observer.protocol.protocol_observer import ProtocolObserver
from nqs_sdk_extension.protocol.cex import CEX
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction


class CEXObserver(ProtocolObserver):
    def __init__(self, protocol: CEX) -> None:
        super().__init__()
        self.cex = protocol

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        # the market observables are already collected by the comptroller - no need to get them separately
        return {}

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        self._observer_id = observable_id

    ######### agent specific    ##############################################################################
    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        return {}

    ######### arbitrage specific ##############################################################################
    def exists_arbitrage_opportunity(self, block_number: int, block_timestamp: int) -> bool:
        return False

    def create_arbitrage_transactions(
        self, block_number: int, block_timestamp: int, arbitrageur_wallet: Wallet
    ) -> Sequence[ABCTransaction]:
        raise NotImplementedError

    def agents_id_to_update(self) -> list[str]:
        raise NotImplementedError
