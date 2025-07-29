from decimal import Decimal
from typing import Any

from nqs_pycore import MutSharedState, SimulationClock, TxRequest, Wallet

from nqs_sdk.bindings.protocols.cex.cex_transactions import CEXRebalanceTransaction
from nqs_sdk.interfaces.protocol import Protocol


def compute_cex_target_amounts(
    token0_balance: Decimal,
    token1_balance: Decimal,
    weight_0: Decimal,
    weight_1: Decimal,
    execution_price: Decimal,
    fee: Decimal,
) -> tuple[Decimal, Decimal]:
    total_value_in_token0 = token0_balance + (token1_balance / execution_price)

    target_token0 = total_value_in_token0 * weight_0
    target_token1 = (total_value_in_token0 * weight_1) * execution_price

    # Calculate differences between current and target
    token0_diff = target_token0 - token0_balance
    token1_diff = target_token1 - token1_balance

    if fee > 0:
        fee_amount0 = abs(token0_diff) * fee
        fee_amount1 = abs(token1_diff) * fee
        target_token0 -= fee_amount0 if token0_diff > 0 else 0
        target_token1 -= fee_amount1 if token1_diff > 0 else 0

    return target_token0, target_token1


class CEXProtocol(Protocol):
    def __init__(self) -> None:
        pass

    def id(self) -> str:
        return "cex"

    def build_tx_payload(self, source: str, sender: str, call: Any) -> TxRequest:
        pass

    def execute_tx(self, clock: SimulationClock, state: MutSharedState, tx: TxRequest) -> None:
        transaction = tx.payload

        wallet = state.get_wallet(tx.sender)
        holdings = {key: Decimal(wallet.get_balance_of_float(key)) for key in wallet.holdings.keys()}

        if isinstance(transaction, CEXRebalanceTransaction):
            token0 = transaction.token0
            token1 = transaction.token1
            weight0 = transaction.weight0
            weight1 = transaction.weight1
            execution_price = transaction.current_price  # price of token0 in terms of token1
            fee = transaction.fee

            # normalize weights
            weight0 = weight0 / (weight0 + weight1)
            weight1 = weight1 / (weight0 + weight1)

            # Use self.fee instead of transaction.fee which doesn't exist in CEXRebalanceTransaction
            token0_balance = holdings[token0]
            token1_balance = holdings[token1]

            target_token0, target_token1 = compute_cex_target_amounts(
                token0_balance, token1_balance, weight0, weight1, execution_price, fee
            )

            # Update holdings with new balanced amounts
            holdings[token0] = target_token0
            holdings[token1] = target_token1

        new_wallet = Wallet(
            holdings=holdings,
            tokens_metadata=wallet.tokens_metadata,
            erc721_tokens=wallet.get_erc721_tokens(),
            agent_name=wallet.agent_name,
        )
        state.insert_wallet(tx.sender, new_wallet)
