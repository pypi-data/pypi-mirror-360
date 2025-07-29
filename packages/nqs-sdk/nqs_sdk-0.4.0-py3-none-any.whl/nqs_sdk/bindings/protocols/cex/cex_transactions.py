from decimal import Decimal

from nqs_pycore import TxRequest

from nqs_sdk.bindings.tx_generators.abstract_transaction import Transaction


class CEXRebalanceTransaction(Transaction):
    token0: str
    token1: str
    weight0: Decimal
    weight1: Decimal
    current_price: Decimal
    fee: Decimal

    def __init__(
        self,
        token0: str,
        token1: str,
        weight0: float | Decimal,
        weight1: float | Decimal,
        current_price: float | Decimal,
        fee: float | Decimal,
    ) -> None:
        self.token0 = token0
        self.token1 = token1
        self.weight0 = Decimal(weight0)
        self.weight1 = Decimal(weight1)
        self.current_price = Decimal(current_price)
        self.fee = Decimal(fee)

    def to_tx_request(self, protocol: str, source: str, sender: str, order: float = 0.0) -> TxRequest:
        return TxRequest.new_with_order(protocol="cex", sender=sender, source=source, payload=self, order=order)
