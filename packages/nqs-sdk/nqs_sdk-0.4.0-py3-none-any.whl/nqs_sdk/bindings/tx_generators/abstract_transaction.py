from abc import ABC, abstractmethod

from nqs_pycore import TxRequest


class Transaction(ABC):
    @abstractmethod
    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest: ...
