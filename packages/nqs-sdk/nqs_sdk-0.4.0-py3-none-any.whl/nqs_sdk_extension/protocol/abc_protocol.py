import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from nqs_pycore import Wallet

from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.wallet.utils import InsufficientBalancesError


class ABCProtocol(ABC):
    def __init__(self, state: ABCProtocolState, gas_fee: int = 0, gas_fee_ccy: Optional[str] = None):
        self._protocol_id = ""
        self.id = state.id
        self.name = state.name
        self.logger = logging.getLogger("Protocol: " + self.name)
        self.logger_key_tx = "Transaction"
        self.gas_fee = gas_fee
        self.gas_fee_ccy = gas_fee_ccy

    def set_environment(self, env_protocol_id: str) -> None:
        self._protocol_id = env_protocol_id

    def spots_to_inject(self, trx: ABCTransaction) -> list[tuple[str, str]]:
        return []

    def inject_spot_values(self, timestamp: int, spots: dict[tuple[str, str], float]) -> None:
        pass

    def charge_gas_fee(self, wallet: Wallet) -> bool:
        """
        Charge gas fees to the wallet -  it could be extended by derived protocols to charge differently according to
        the type of transaction
        :param wallet:
        :return: returns True if the operation was successful, False otherwise
        """
        if self.gas_fee == 0 or self.gas_fee_ccy is None:
            return True

        try:
            wallet.transfer_from(self.gas_fee_ccy, self.gas_fee)
        except InsufficientBalancesError:
            return False

        return True

    ########################### ABSTRACT METHODS ######################################################

    @abstractmethod
    def process_single_transaction(self, transaction: ABCTransaction) -> None:
        pass

    @abstractmethod
    def process_transactions(self, transactions: list[ABCTransaction]) -> None:
        pass

    @abstractmethod
    def get_state(self, *args: Any) -> ABCProtocolState:
        pass

    @abstractmethod
    def restore_from_state(self, state: ABCProtocolState) -> None:
        pass

    # TODO: implement __repr__ and __str__
