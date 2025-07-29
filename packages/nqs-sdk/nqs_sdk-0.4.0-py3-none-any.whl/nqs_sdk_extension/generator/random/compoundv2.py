from decimal import Decimal
from typing import Any

from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.generator.random.random_transaction_generator import RandomTransactionGenerator
from nqs_sdk_extension.observer.protocol.compoundv2 import Compoundv2MarketObserver
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.compoundv2 import (
    BorrowTransactionCompv2,
    MintTransactionCompv2,
    ParamsCompoundv2ActionType,
    RedeemTransactionCompv2,
    RepayBorrowTransactionCompv2,
)


class RandomCompoundv2Generator(RandomTransactionGenerator):
    def __init__(
        self,
        id: int,
        name: str,
        type: str,
        random_generation_parameters: dict,
        random_generator: RandomGenerator,
        mapping_block_timestamps: dict[int, int],
        additional_params: dict,
    ):
        super().__init__(id, name, type, random_generation_parameters, random_generator, mapping_block_timestamps)
        self.additional_parameters = additional_params
        self.ctoken = self.additional_parameters["ctoken"]
        self._transaction_types = [transaction_type.value for transaction_type in ParamsCompoundv2ActionType]
        self._observer: Compoundv2MarketObserver
        # Exclude transfer and liquidate transactions from the random generation
        self._transaction_types = [
            transaction_type.value
            for transaction_type in ParamsCompoundv2ActionType
            if (
                transaction_type.value != ParamsCompoundv2ActionType.TRANSFER.value
                and transaction_type.value != ParamsCompoundv2ActionType.LIQUIDATE.value
            )
        ]

    def validate_observer(self) -> None:
        if not isinstance(self._observer, Compoundv2MarketObserver):
            raise ValueError("The observer is not of the correct type")

    def generate_mint_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        decimals = self._observer.underlying_decimals
        amount_args = {"amount": value_dict.get("amount", None), "pct_of_market": value_dict.get("pct_of_market", None)}
        if (amount_args["amount"] is None) == (amount_args["pct_of_market"] is None):
            raise ValueError("Either pct_of_market or amount must be provided")

        if amount_args["pct_of_market"] is not None:
            amount = round(self._observer._compound_market.total_cash * amount_args["pct_of_market"])
        else:
            amount = round(Decimal(amount_args["amount"]).scaleb(decimals))

        return MintTransactionCompv2(
            block_number=block_number,
            protocol_id=self.type,
            ctoken=self.ctoken,
            sender_wallet=None,
            mint_amount=amount,
        )

    def generate_redeem_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        amount: int = 0
        tokens: int = 0
        decimals = self._observer.underlying_decimals
        amount_args = {"amount": value_dict.get("amount", None), "pct_of_market": value_dict.get("pct_of_market", None)}
        if (amount_args["amount"] is None) == (amount_args["pct_of_market"] is None):
            raise ValueError("Either pct_of_market or amount must be provided")

        if amount_args["pct_of_market"] is not None:
            tokens = round(self._observer._compound_market.total_supply * amount_args["pct_of_market"])
        else:
            amount = round(Decimal(amount_args["amount"]).scaleb(decimals))

        return RedeemTransactionCompv2(
            block_number=block_number,
            protocol_id=self.type,
            ctoken=self.ctoken,
            sender_wallet=None,
            redeem_tokens_in=tokens,
            redeem_amount_in=amount,
        )

    def generate_borrow_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        decimals = self._observer.underlying_decimals
        amount_args = {"amount": value_dict.get("amount", None), "pct_of_market": value_dict.get("pct_of_market", None)}
        if (amount_args["amount"] is None) == (amount_args["pct_of_market"] is None):
            raise ValueError("Either pct_of_market or amount must be provided")

        if amount_args["pct_of_market"] is not None:
            amount = round(self._observer._compound_market.total_borrows * amount_args["pct_of_market"])
        else:
            amount = round(Decimal(amount_args["amount"]).scaleb(decimals))

        return BorrowTransactionCompv2(
            block_number=block_number,
            protocol_id=self.type,
            ctoken=self.ctoken,
            sender_wallet=None,
            borrow_amount=amount,
        )

    def generate_repay_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        decimals = self._observer.underlying_decimals
        amount_args = {"amount": value_dict.get("amount", None), "pct_of_market": value_dict.get("pct_of_market", None)}
        if (amount_args["amount"] is None) == (amount_args["pct_of_market"] is None):
            raise ValueError("Either pct_of_market or amount must be provided")

        if amount_args["pct_of_market"] is not None:
            amount = round(self._observer._compound_market.total_borrows * amount_args["pct_of_market"])
        else:
            amount = round(Decimal(amount_args["amount"]).scaleb(decimals))

        return RepayBorrowTransactionCompv2(
            block_number=block_number,
            protocol_id=self.type,
            ctoken=self.ctoken,
            sender_wallet=None,
            borrow_wallet=None,
            repay_amount=amount,
        )

    def generate_liquidate_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        raise NotImplementedError("This method is not implemented for RandomCompoundv2Generator")

    def generate_transfer_transactions_at_block(self, block_number: int, value_dict: dict) -> ABCTransaction:
        raise NotImplementedError("This method is not implemented for RandomCompoundv2Generator")

    @property
    def transaction_types(self) -> list[str]:
        return self._transaction_types

    def generate_transaction_at_block(self, transaction_type: str, **kwargs: Any) -> ABCTransaction:
        match transaction_type:
            case ParamsCompoundv2ActionType.MINT.value:
                return self.generate_mint_transactions_at_block(**kwargs)
            case ParamsCompoundv2ActionType.REDEEM.value:
                return self.generate_redeem_transactions_at_block(**kwargs)
            case ParamsCompoundv2ActionType.BORROW.value:
                return self.generate_borrow_transactions_at_block(**kwargs)
            case ParamsCompoundv2ActionType.REPAY_BORROW.value:
                return self.generate_repay_transactions_at_block(**kwargs)
            case ParamsCompoundv2ActionType.LIQUIDATE.value:
                return self.generate_liquidate_transactions_at_block(**kwargs)
            case ParamsCompoundv2ActionType.TRANSFER.value:
                return self.generate_transfer_transactions_at_block(**kwargs)
            case _:
                raise ValueError(f"Invalid transaction type: {transaction_type}")
