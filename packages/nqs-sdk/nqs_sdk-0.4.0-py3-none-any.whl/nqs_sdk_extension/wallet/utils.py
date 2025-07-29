from decimal import Decimal


def rescale_to_int(value: int | float, decimals: int) -> int:
    return int(round(Decimal(value).scaleb(decimals)))

    # TODO: should be initialized from a state!
    # TODO: ERC721.token_id should be unique, so we can use it as a key in a dictionary


class InsufficientBalancesError(Exception):
    """Exception raised for insufficient balances in agent's wallet.

    Attributes:
        amount_attempted_to_transfer -- amount of tokens attempted to transfer
        token_symbol -- symbol of the token that was tried to be transferred
        token_balance -- wallet's balance in the token
    """

    def __init__(
        self,
        amount_attempted_to_transfer: float,
        token_symbol: str,
        token_balance: float,
        agent_name: str,
        action_name: str | None,
    ) -> None:
        message = (
            f"User '{agent_name}' : Insufficient Balances - "
            f"Cannot transfer {amount_attempted_to_transfer} {token_symbol} "
            f"from wallet, wallet's balance is only {token_balance} {token_symbol}."
        )
        super().__init__(message)


class OverflowBalanceError(Exception):
    """Exception raised for overflow balances in agent's wallet.

    Attributes:
        amount_attempted_to_transfer -- amount of tokens attempted to transfer
        token_symbol -- symbol of the token that was tried to be transferred
        token_balance -- wallet's balance in the token
    """

    def __init__(
        self, amount_attempted_to_transfer: float, token_symbol: str, token_balance: float, action_name: str | None
    ) -> None:
        message = (
            f"Overflow error - Cannot transfer {amount_attempted_to_transfer}{token_symbol} to the wallet. "
            f"The wallet balance is {token_balance} and adding the transfer amount would reuslt in a overflow"
        )
        super().__init__(message)


class MissingERC721Error(Exception):
    """Exception raised when the required ERC721 token is not found.

    Attributes:
        token_id -- ID of the ERC721 token that was tried to be accessed
        agent_name -- name of the agent that tried to access the token
    """

    def __init__(self, token_id: str, agent_name: str, action_name: str | None) -> None:
        message = (
            f"Missing ERC721 Token - Cannot find token with ID '{token_id}' " f"for agent with name '{agent_name}'"
        )
        super().__init__(message)


class InsufficientLiquidityError(Exception):
    """Exception raised when the required ERC721 token has not enough liquidity to perform the attempted burn
     transaction

    Attributes:
        token_id -- ID of the ERC721 token that was tried to be accessed
        agent_name -- name of the agent that tried to access the token
    """

    def __init__(self, token_id: str, agent_name: str, action_name: str | None) -> None:
        message = (
            f"Failed to execute the burn transaction on token with ID '{token_id}' of '{agent_name}'. Trying to "
            f"remove more than the total amount of liquidity available."
        )
        super().__init__(message)


class AgentLiquidityError(Exception):
    """Exception raised when an agent's swap empties a univ3 pool

    Attributes:
        agent_name -- name of the agent that tried to access the token
        action_name -- name of the action that the agent tried to perform
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AmountNoneError(Exception):
    """Exception raised when amount, amount0 and amount1 are all set to None"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class WrongTickRangeError(Exception):
    """Exception raised when attempting to modify an existing LP position on a wrong tick range"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TickInitializationError(Exception):
    """Exception raised when the tick range is not initialized correctly"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TokenAlreadyExistsError(Exception):
    """Exception raised when attempting to add a token that already exists in the wallet"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class LiquidityRangeError(Exception):
    """Exception raised when an agent is trying to provide liquidity in a wrong range"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TickRangeError(Exception):
    """Exception raised when an agent is trying to provide liquidity in a wrong range"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
