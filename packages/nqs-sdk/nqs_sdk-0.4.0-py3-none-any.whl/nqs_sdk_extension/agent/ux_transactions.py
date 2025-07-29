from nqs_pycore import Wallet

from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction


class UXTransaction(ABCTransaction):
    """
    A class to represent a transaction from the user interface.
    """

    def __init__(self, args_tx: dict, sender_wallet: Wallet) -> None:
        self.sender_wallet = sender_wallet
        for key, value in args_tx.items():
            if value is not None:
                setattr(self, key, value)
