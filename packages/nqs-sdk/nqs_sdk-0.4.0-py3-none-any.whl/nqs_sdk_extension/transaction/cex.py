from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

import numpy as np
from micro_language import Expression

from nqs_sdk_extension.token_utils import wrap_token
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.transaction_helper import ProtocolTransactionHelper
from nqs_sdk_extension.wallet import rescale_to_int

TOLERANCE = 10**-8


class CEXTransactionType(Enum):
    SWAP = "Swap"
    REBALANCE = "rebalance"


class ParamsCEXTransactionType(Enum):
    SWAP = "swap"
    REBALANCE = "rebalance"


@dataclass
class TransactionCEX(ABCTransaction):
    action_type: CEXTransactionType = field(init=False)


@dataclass
class SwapTransactionCEX(TransactionCEX):
    token_to_sell: str  # The symbol of the token to swap out
    token_to_buy: str  # The symbol of the token to swap in
    amount_to_buy: int | Expression | None = None  # The amount of token_to_buy to swap in
    amount_to_sell: int | Expression | None = None  # The amount of token_to_sell to swap out

    def __post_init__(self) -> None:
        self.action_type = CEXTransactionType.SWAP
        self.token_to_sell = wrap_token(self.token_to_sell)
        self.token_to_buy = wrap_token(self.token_to_buy)


@dataclass
class RebalanceTransactionCEX(TransactionCEX):
    weights: dict[str, float]  # The weights of the tokens to rebalance

    def __post_init__(self) -> None:
        self.action_type = CEXTransactionType.REBALANCE
        for token in self.weights.keys():
            new_weights = {}
            for token in self.weights.keys():
                new_weights[wrap_token(token)] = self.weights[token]
            self.weights = new_weights


# mypy: ignore-errors
class TransactionHelperCEX(ProtocolTransactionHelper):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def create_swap_transaction(**kwargs) -> SwapTransactionCEX:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "amount_to_buy": None,
            "token_to_buy": None,
            "amount_to_sell": None,
            "token_to_sell": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a SwapTransaction object
        swap_transaction = SwapTransactionCEX(**fields)
        return swap_transaction

    @staticmethod
    def create_rebalance_transaction(**kwargs) -> RebalanceTransactionCEX:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "weights": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)

        if sum(fields["weights"].values()) != 1:
            # check if within tolerance
            if np.abs(sum(fields["weights"].values()) - 1) < TOLERANCE and all(
                0 <= _ <= 1 for _ in fields["weights"].values()
            ):
                fields["weights"] = {k: round(v, 8) for k, v in fields["weights"].items()}
            else:
                raise ValueError(
                    f"Weights of rebalance transaction must sum to 1, got {sum(fields['weights'].values())}"
                )
        # Create a RebalanceTransaction object
        rebalance_transaction = RebalanceTransactionCEX(**fields)
        return rebalance_transaction

    @property
    def mapping_action_helper(self) -> dict[str, Callable[[dict], ABCTransaction]]:
        return {
            ParamsCEXTransactionType.SWAP.value: self.create_swap_transaction,
            ParamsCEXTransactionType.REBALANCE.value: self.create_rebalance_transaction,
        }

    def convert_amounts_to_integers(self, transaction: TransactionCEX, **kwargs: str) -> TransactionCEX:
        if isinstance(transaction, SwapTransactionCEX):
            # check that symbol0 and symbol1 are in the kwargs
            token_to_buy, token_to_sell = transaction.token_to_buy, transaction.token_to_sell
            if token_to_buy is None or token_to_sell is None:
                raise ValueError("token_to_buy or token_to_sell is None")
            wallet = transaction.sender_wallet
            if wallet is None:
                raise ValueError("Wallet is None")
            decimal_in = wallet._tokens_metadata[token_to_buy].decimals
            decimals_out = wallet._tokens_metadata[token_to_sell].decimals

            transaction.amount_to_buy = (
                rescale_to_int(transaction.amount_to_buy, decimal_in) if transaction.amount_to_buy is not None else None
            )
            transaction.amount_to_sell = (
                rescale_to_int(transaction.amount_to_sell, decimals_out)
                if transaction.amount_to_sell is not None
                else None
            )
            return transaction
        elif isinstance(transaction, RebalanceTransactionCEX):
            return transaction
        else:
            raise ValueError("Unrecognized CEX transaction")
