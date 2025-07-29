from abc import ABC, abstractmethod
from typing import Any, Callable

from nqs_pycore import Wallet

from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction


class ProtocolTransactionHelper(ABC):
    def __init__(self) -> None:
        pass

    def generate_transactions_from_user_params(
        self, action: str, args_tx: dict, sender_wallet: Wallet, **kwargs: Any
    ) -> ABCTransaction:
        if self.mapping_action_helper.get(action, None) is not None:
            args_tx.update({"sender_wallet": sender_wallet})
            transaction = self.mapping_action_helper[action](**args_tx)
            return self.convert_amounts_to_integers(transaction, **kwargs)
        else:
            raise ValueError(f"Unsupported action - {action}")

    @property
    @abstractmethod
    def mapping_action_helper(self) -> dict[str, Callable[[], ABCTransaction]]:
        pass

    @abstractmethod
    def convert_amounts_to_integers(self, transaction: ABCTransaction, **kwargs: Any) -> ABCTransaction:
        pass
