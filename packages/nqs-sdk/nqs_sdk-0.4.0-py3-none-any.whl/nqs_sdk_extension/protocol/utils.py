from typing import Any, Callable

from nqs_pycore import Wallet

from nqs_sdk_extension.protocol.abc_protocol import ABCProtocol
from nqs_sdk_extension.wallet.arbitrageur_wallet import ArbitrageurWallet
from nqs_sdk_extension.wallet.utils import (
    AgentLiquidityError,
    InsufficientBalancesError,
    InsufficientLiquidityError,
    LiquidityRangeError,
    MissingERC721Error,
    OverflowBalanceError,
    TickInitializationError,
    TickRangeError,
)


def bitwise_and(a: int, b: int) -> int:
    return a & b


def bitwise_or(a: int, b: int) -> int:
    return a | b


def shift(value: int, positions: int) -> int:
    if positions >= 0:
        return value << positions
    else:
        return value >> abs(positions)


def rollback_on_failure(method: Callable) -> Callable:
    def wrapper(self: ABCProtocol, *args: Any, **kwargs: Any) -> Any:
        msg_sender: Wallet = kwargs["msg_sender"]
        block_timestamp = kwargs.get("block_timestamp")
        block_number = kwargs.get("block_number")
        action_name = kwargs.get("action_name")

        # only snapshot if it is an action from the agent
        if not isinstance(msg_sender, Wallet) or isinstance(msg_sender, ArbitrageurWallet):
            # Call the original method
            result = method(self, *args, **kwargs)
            return result
        else:
            # then backup states
            wallet_state = msg_sender.get_state()
            protocol_state = self.get_state(block_timestamp)

            try:
                # Call the original method
                result = method(self, *args, **kwargs)

            except (
                InsufficientBalancesError,
                OverflowBalanceError,
                MissingERC721Error,
                InsufficientLiquidityError,
                AgentLiquidityError,
                LiquidityRangeError,
                TickRangeError,
                TickInitializationError,
                Exception,
            ) as e:
                allowed_error_messages = {"insufficient balance", "insufficient liquidity"}
                allwed_exceptions: list[type] = [
                    InsufficientBalancesError,
                    OverflowBalanceError,
                    MissingERC721Error,
                    InsufficientLiquidityError,
                    AgentLiquidityError,
                    LiquidityRangeError,
                    TickRangeError,
                    TickInitializationError,
                ]
                if isinstance(e, Exception) and type(e) not in allwed_exceptions:
                    error_msg = str(e).lower()
                    if not any(msg in error_msg for msg in allowed_error_messages):
                        raise e

                # Rollback the state to the previous state
                transaction = kwargs.get("transaction", {})
                if transaction:
                    block_number = transaction.block_number
                    block_timestamp = transaction.block_timestamp
                    action_name = transaction.action_name

                message = f"Action {action_name} - " + str(e) if action_name is not None else str(e)
                self.logger.warning(
                    f"Key: FailureRollback - Timestamp: {block_timestamp} - Block number: {block_number} - "
                    f"Agent: {msg_sender.agent_name} - Transaction: {kwargs.get('transaction')} - Error: {message}"
                )
                # Rollback the state to the previous state
                self.restore_from_state(protocol_state)
                msg_sender.restore_from_state(wallet_state)

            else:
                return result

    return wrapper
