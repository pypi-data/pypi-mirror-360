from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from micro_language import Expression
from nqs_pycore import Wallet

from nqs_sdk_extension.token_utils import wrap_token
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.transaction_helper import ProtocolTransactionHelper
from nqs_sdk_extension.wallet import rescale_to_int


class Compoundv2TransactionType(Enum):
    MINT = "DepositCollateral"
    REDEEM = "RedeemCollateral"
    BORROW = "Borrow"
    REPAY_BORROW = "RepayBorrow"
    LIQUIDATE = "Liquidate"
    TRANSFER = "Transfer"


class ParamsCompoundv2ActionType(Enum):
    MINT = "mint"
    REDEEM = "redeem"
    BORROW = "borrow"
    REPAY_BORROW = "repay"
    LIQUIDATE = "liquidate"
    TRANSFER = "transfer"


@dataclass
class TransactionCompoundv2(ABCTransaction):
    ctoken: str
    action_type: Compoundv2TransactionType = field(init=False)


# Define the sub-objects
@dataclass
class MintTransactionCompv2(TransactionCompoundv2):
    mint_amount: int | Expression

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.MINT
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])


@dataclass
class RedeemTransactionCompv2(TransactionCompoundv2):
    redeem_tokens_in: int | Expression
    redeem_amount_in: int | Expression

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.REDEEM
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])


@dataclass
class BorrowTransactionCompv2(TransactionCompoundv2):
    borrow_amount: int | Expression

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.BORROW
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])


@dataclass
class RepayBorrowTransactionCompv2(TransactionCompoundv2):
    repay_amount: int | Expression
    borrow_wallet: Wallet | None

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.REPAY_BORROW
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])


@dataclass
class LiquidateTransactionCompv2(TransactionCompoundv2):
    borrower: Wallet | None
    repay_amount: int | Expression
    ctoken_collateral: str

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.LIQUIDATE
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])
        self.ctoken_collateral = "c" + wrap_token(self.ctoken_collateral.split("c")[1])


@dataclass
class TransferTransactionCompv2(TransactionCompoundv2):
    dst_wallet: Wallet | None
    amount: int | Expression

    def __post_init__(self) -> None:
        self.action_type = Compoundv2TransactionType.TRANSFER
        self.ctoken = "c" + wrap_token(self.ctoken.split("c")[1])


# XXX: Difficult to type hint these methods because of the **kwargs
# mypy: ignore-errors
class TransactionHelperCompoundv2(ProtocolTransactionHelper):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def create_mint_transaction(**kwargs) -> MintTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "mint_amount": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        mint_transaction = MintTransactionCompv2(**fields)
        return mint_transaction

    @staticmethod
    def create_redeem_transaction(**kwargs) -> RedeemTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "redeem_tokens_in": None,
            "redeem_amount_in": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        redeem_transaction = RedeemTransactionCompv2(**fields)
        return redeem_transaction

    @staticmethod
    def create_borrow_transaction(**kwargs) -> BorrowTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "borrow_amount": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        borrow_transaction = BorrowTransactionCompv2(**fields)
        return borrow_transaction

    @staticmethod
    def create_repay_transaction(**kwargs) -> RepayBorrowTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "repay_amount": None,
            "borrow_wallet": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        if fields["borrow_wallet"] is None:
            fields["borrow_wallet"] = fields["sender_wallet"]
        # Create a MintTransaction object
        repay_transaction = RepayBorrowTransactionCompv2(**fields)
        return repay_transaction

    @staticmethod
    def create_liquidate_transaction(**kwargs) -> LiquidateTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "borrower": None,
            "repay_amount": None,
            "ctoken_collateral": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        liquidate_transaction = LiquidateTransactionCompv2(**fields)
        return liquidate_transaction

    @staticmethod
    def create_transfer_transaction(**kwargs) -> TransferTransactionCompv2:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "amount": None,
            "dst_wallet": None,
            "ctoken": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        transfer_transaction = TransferTransactionCompv2(**fields)
        return transfer_transaction

    @property
    def mapping_action_helper(self) -> dict[str, Callable[[dict], ABCTransaction]]:
        return {
            ParamsCompoundv2ActionType.MINT.value: self.create_mint_transaction,
            ParamsCompoundv2ActionType.REDEEM.value: self.create_redeem_transaction,
            ParamsCompoundv2ActionType.BORROW.value: self.create_borrow_transaction,
            ParamsCompoundv2ActionType.REPAY_BORROW.value: self.create_repay_transaction,
            ParamsCompoundv2ActionType.LIQUIDATE.value: self.create_liquidate_transaction,
            ParamsCompoundv2ActionType.TRANSFER.value: self.create_transfer_transaction,
        }

    def convert_amounts_to_integers(self, transaction: TransactionCompoundv2, **kwargs) -> TransactionCompoundv2:
        wallet = transaction.sender_wallet
        ctoken_metadata = wallet.get_py_metadata(transaction.ctoken)
        if wallet is None:
            raise ValueError("Wallet is None")
        if isinstance(transaction, MintTransactionCompv2):
            transaction.mint_amount = rescale_to_int(-transaction.mint_amount, ctoken_metadata.decimals)
        elif isinstance(transaction, RedeemTransactionCompv2):
            transaction.redeem_amount_in = (
                rescale_to_int(transaction.redeem_amount_in, ctoken_metadata.decimals)
                if transaction.redeem_amount_in is not None
                else 0
            )
            transaction.redeem_tokens_in = (
                rescale_to_int(transaction.redeem_tokens_in, ctoken_metadata.decimals)
                if transaction.redeem_tokens_in is not None
                else 0
            )
        elif isinstance(transaction, BorrowTransactionCompv2):
            transaction.borrow_amount = rescale_to_int(transaction.borrow_amount, ctoken_metadata.decimals)
        elif isinstance(transaction, RepayBorrowTransactionCompv2):
            transaction.repay_amount = rescale_to_int(transaction.repay_amount, ctoken_metadata.decimals)
        elif isinstance(transaction, LiquidateTransactionCompv2):
            transaction.repay_amount = rescale_to_int(transaction.repay_amount, ctoken_metadata.decimals)
        elif isinstance(transaction, TransferTransactionCompv2):
            transaction.amount = rescale_to_int(transaction.amount, ctoken_metadata.decimals)
        return transaction
