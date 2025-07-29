import copy
from decimal import Decimal
from typing import Optional

from nqs_pycore import Wallet

from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.state import ABCProtocolState, StateCEX
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.cex import RebalanceTransactionCEX as RebalanceTransactionCEX
from nqs_sdk_extension.transaction.cex import SwapTransactionCEX as SwapTransactionCEX
from nqs_sdk_extension.transaction.cex import TransactionCEX


class CEX(ABCProtocol):
    """
    Class used to exchange tokens at market price
    """

    def __init__(self, state: StateCEX, gas_fee: int = 0, gas_fee_ccy: Optional[str] = None):
        # gas fees are not applicable to "CEX protocol"
        super().__init__(state, 0, None)
        self.numeraire = state.numeraire
        self.stored_spot: dict[tuple[str, str], float] = {}

    def process_single_transaction(self, transaction: ABCTransaction) -> None:
        if not isinstance(transaction, TransactionCEX):
            message = "Unrecognized CEX transaction"
            message = (
                f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
            )
            raise ValueError(message)
        self._handle_transaction(transaction)

    def _handle_transaction(self, transaction: TransactionCEX) -> None:
        if isinstance(transaction, SwapTransactionCEX):
            self._handle_swap(transaction)
        elif isinstance(transaction, RebalanceTransactionCEX):
            self._handle_rebalance(transaction)
        else:
            message = "Unrecognized CEX transaction"
            message = (
                f"Action {transaction.action_name} - " + message if transaction.action_name is not None else message
            )
            raise ValueError(message)

    def _handle_swap(self, transaction: SwapTransactionCEX) -> None:
        if transaction.sender_wallet is None:
            raise ValueError("CEX does not accept simulated users transactions")
        msg_sender = transaction.sender_wallet
        token_to_buy = transaction.token_to_buy
        token_to_sell = transaction.token_to_sell

        if transaction.amount_to_sell == 0 or transaction.amount_to_buy == 0:
            return

        amount_to_buy = (
            transaction.amount_to_buy
            if transaction.amount_to_buy is not None
            else round(
                Decimal(transaction.amount_to_sell).scaleb(-msg_sender._tokens_metadata[token_to_sell].decimals)  # type: ignore
                * Decimal(self.stored_spot[(token_to_sell, token_to_buy)]).scaleb(
                    msg_sender._tokens_metadata[token_to_buy].decimals
                )
            )
        )
        amount_to_sell = (
            transaction.amount_to_sell
            if transaction.amount_to_sell is not None
            else round(
                Decimal(transaction.amount_to_buy).scaleb(-msg_sender._tokens_metadata[token_to_buy].decimals)  # type: ignore
                * Decimal(self.stored_spot[(token_to_buy, token_to_sell)]).scaleb(
                    msg_sender._tokens_metadata[token_to_sell].decimals
                )
            )
        )

        if not msg_sender.check_has_enough_balance(
            amount=amount_to_sell, symbol=token_to_sell, action_name=transaction.action_name, raise_warning=True
        ):
            return

        msg_sender.transfer_from(token_to_sell, amount_to_sell, transaction.action_name)
        msg_sender.transfer_to(token_to_buy, amount_to_buy, transaction.action_name)

        # log and create event
        self.logger.debug(
            f"SWAP: amount_to_buy: {amount_to_buy}, amount_to_sell: {amount_to_sell}, "
            f"token_to_buy: {token_to_buy}, token_to_sell: {token_to_sell}",
        )

    def _handle_rebalance(self, transaction: RebalanceTransactionCEX) -> None:
        if transaction.sender_wallet is None:
            raise ValueError("CEX does not accept simulated users transactions")
        msg_sender = transaction.sender_wallet

        rebalance_wallet_total_value_in_numeraire = self.get_token_list_total_value_in_numeraire(
            msg_sender, list(transaction.weights.keys())
        )
        numeraire_decimals = msg_sender._tokens_metadata[self.numeraire].decimals
        for token in transaction.weights.keys():
            token_decimals = msg_sender._tokens_metadata[token].decimals
            numeraire_target_value = rebalance_wallet_total_value_in_numeraire * transaction.weights[token]
            token_amount = round(
                Decimal(numeraire_target_value).scaleb(token_decimals - numeraire_decimals)
                / Decimal(self.stored_spot[(token, self.numeraire)])
            )
            token_balance = round(msg_sender.get_balance_of(token))
            if token_amount > token_balance:
                msg_sender.transfer_to(token, token_amount - token_balance, transaction.action_name)
            else:
                msg_sender.transfer_from(token, token_balance - token_amount, transaction.action_name)

        # log and create event
        self.logger.debug(
            f"REBALANCE: {transaction.weights}",
        )

        new_rebalance_wallet_total_value_in_numeraire = self.get_token_list_total_value_in_numeraire(
            msg_sender, list(transaction.weights.keys())
        )

        if abs(new_rebalance_wallet_total_value_in_numeraire / rebalance_wallet_total_value_in_numeraire - 1) > 1.0e-3:
            message = (
                f"Rebalance : {transaction} failed"
                if transaction.action_name is None
                else f"Action {transaction.action_name} - Rebalance : {transaction} failed"
            )
            raise ValueError(message)

    def get_token_list_total_value_in_numeraire(self, wallet: Wallet, token_list: list[str]) -> int:
        rebalance_wallet_total_value_in_numeraire = 0
        numeraire_decimals = wallet._tokens_metadata[self.numeraire].decimals
        for token in token_list:
            token_decimals = wallet._tokens_metadata[token].decimals
            rebalance_wallet_total_value_in_numeraire += round(
                Decimal(wallet.get_balance_of(token)).scaleb(-token_decimals)
                * Decimal(self.stored_spot[(token, self.numeraire)]).scaleb(numeraire_decimals)
            )
        return rebalance_wallet_total_value_in_numeraire

    def spots_to_inject(self, trx: ABCTransaction) -> list[tuple[str, str]]:
        if isinstance(trx, SwapTransactionCEX):
            if trx.amount_to_buy is None:
                return [(trx.token_to_sell, trx.token_to_buy)]
            else:
                return [(trx.token_to_buy, trx.token_to_sell)]
        elif isinstance(trx, RebalanceTransactionCEX):
            spots_to_inject = []
            for token in trx.weights.keys():
                spots_to_inject.append((token, self.numeraire))
            return spots_to_inject
        else:
            message = "Unrecognized CEX transaction"
            message = f"Action {trx.action_name} - " + message if trx.action_name is not None else message
            raise ValueError(message)

    def inject_spot_values(self, timestamp: int, spot_values: dict[tuple[str, str], float]) -> None:
        self.stored_spot = spot_values

    def process_transactions(self, transactions: list[ABCTransaction]) -> None:
        for transaction in transactions:
            self.process_single_transaction(transaction)

    def get_state(self, block_timestamp: int) -> StateCEX:
        state = StateCEX(
            id=self.id, block_number=0, block_timestamp=block_timestamp, name=self.name, numeraire=self.numeraire
        )
        state = copy.deepcopy(state)
        return state

    def restore_from_state(self, state: ABCProtocolState) -> None:
        if isinstance(state, StateCEX):
            super().__init__(state)
        else:
            raise ValueError(f"States of the class {state.__class__} cannot restore a CEX...")

    def charge_gas_fee(self, wallet: Wallet) -> bool:
        """
        CEX does not charge gas fees as of now
        :param wallet:
        :return:
        """
        return True
