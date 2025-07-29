import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Callable, TypeAlias

from micro_language import Expression

from nqs_sdk_extension.constants import ADJUST_MINT_AMOUNTS
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.utils import calculate_amounts
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.transaction_helper import ProtocolTransactionHelper
from nqs_sdk_extension.wallet import rescale_to_int

"""
List of events emitted by Uniswap V3 contracts:
https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolEvents

We do not support the current events: Initialize (not needed), Flash
"""

# Type aliases
int24: TypeAlias = int
uint128: TypeAlias = int
uint256: TypeAlias = int
int256: TypeAlias = int
uint160: TypeAlias = int


class Univ3TransactionType(Enum):
    SWAP = "Swap"
    MINT = "Mint"
    BURN = "Burn"
    COLLECT = "Collect"


class ParamsUniv3TransactionType(Enum):
    SWAP = "swap"
    MINT = "mint"
    BURN = "burn"
    COLLECT = "collect"


@dataclass
class TransactionUniv3(ABCTransaction):
    action_type: Univ3TransactionType = field(init=False)


@dataclass
class MintTransactionUniv3(TransactionUniv3):
    tick_lower: int24 | Expression  # The lower tick of the position
    tick_upper: int24 | Expression  # The upper tick of the position
    amount: uint128 | Expression | None = None  # The amount of liquidity minted to the position range
    amount0: uint256 | Expression | None = None  # How much token0 was required for the minted liquidity
    amount1: uint256 | Expression | None = None  # How much token1 was required for the minted liquidity
    token_id: str | None = None  # position ID defined by users in the parameter file

    def __post_init__(self) -> None:
        self.action_type = Univ3TransactionType.MINT


@dataclass
class CollectTransactionUniv3(TransactionUniv3):
    tick_lower: int24 | Expression  # The lower tick of the position
    tick_upper: int24 | Expression  # The upper tick of the position
    # The following two fields are not needed for the moment because we collect ALL the fees available
    amount0: uint128 | Expression | None = None  # The amount of token0 fees requested to collect
    amount1: uint128 | Expression | None = None  # The amount of token1 fees requested to collect
    token_id: str | None = None  # position ID defined by users in the parameter file

    def __post_init__(self) -> None:
        self.action_type = Univ3TransactionType.COLLECT


@dataclass
class BurnTransactionUniv3(TransactionUniv3):
    tick_lower: int24 | Expression  # The lower tick of the position
    tick_upper: int24 | Expression  # The upper tick of the position
    amount: uint128 | Expression | None = None  # The amount of liquidity to remove
    amount0: uint256 | Expression | None = None  # The amount of token0 withdrawn
    amount1: uint256 | Expression | None = None  # The amount of token1 withdrawn
    token_id: str | None = None  # position ID defined by users in the parameter file

    def __post_init__(self) -> None:
        self.action_type = Univ3TransactionType.BURN


@dataclass
class SwapTransactionUniv3(TransactionUniv3):
    # XXX: CUSTOM FORMAT WITH EXPLICIT QUANTITIES IN/OUT
    amount0_in: uint256 | Expression | None = None  # The amount of token0 to swap into the pool
    amount1_in: uint256 | Expression | None = None  # The amount of token1 to swap into the pool
    amount0_out: uint256 | Expression | None = None  # The amount of token0 to swap out of the pool
    amount1_out: uint256 | Expression | None = None  # The amount of token1 to swap out of the pool
    sqrt_price_limit_x96: uint256 | Expression | None = (
        None  # The maximum sqrt(price) of the pool for the swap to succeed
    )
    # The following fields are emitted by the Uniswap V3 contract
    # amount0: int256 | None # The delta of the token0 balance of the pool
    # amount1: int256 | None # The delta of the token1 balance of the pool
    # The following two fields are POST-TRADE values and not used for simulations!
    # sqrtPriceX96: uint160 = None # The sqrt(price) of the pool after the swap, as a Q64.96
    # liquidity: uint128 = None #The liquidity of the pool after the swap
    # tick: int24 = None # The log base 1.0001 of price of the pool after the swap

    def __post_init__(self) -> None:
        self.action_type = Univ3TransactionType.SWAP


# XXX: Difficult to type hint these methods because of the **kwargs
# mypy: ignore-errors
class TransactionHelperUniv3(ProtocolTransactionHelper):
    def __init__(self) -> None:
        super().__init__()
        self.token_id_mapping: dict[(str, str), list[str]] = {}

    @staticmethod
    def adjust_mint_amounts(
        transaction: MintTransactionUniv3, symbol0: str, symbol1: str, sqrt_price: int
    ) -> MintTransactionUniv3:
        user_wallet = transaction.sender_wallet
        wallet_amount0 = user_wallet.holdings.get(symbol0, 0)
        wallet_amount1 = user_wallet.holdings.get(symbol1, 0)
        user_input_amount0 = transaction.amount0
        user_input_amount1 = transaction.amount1
        user_input_amount = transaction.amount
        tick_lower = int(transaction.tick_lower)
        tick_upper = int(transaction.tick_upper)
        decimals0 = user_wallet.tokens_metadata.get(symbol0, {"decimals": 0}).decimals
        decimals1 = user_wallet.tokens_metadata.get(symbol1, {"decimals": 0}).decimals
        sqrt_price_lower = TickMath.tick_to_price(tick_lower, decimals0, decimals1) ** 0.5
        sqrt_price_upper = TickMath.tick_to_price(tick_upper, decimals0, decimals1) ** 0.5

        amount, amount0, amount1 = calculate_amounts(
            sqrt_price_lower,
            sqrt_price,
            sqrt_price_upper,
            user_input_amount0,
            user_input_amount1,
            user_input_amount,
            decimals0,
            decimals1,
        )

        if amount is None and amount0 is None and amount1 is None:
            logging.warning(f"Mint transaction : {transaction} got a wrong amounts/bounds combination")
            return transaction

        if amount0 > wallet_amount0 and amount1 <= wallet_amount1:
            new_amount, new_amount0, new_amount1 = calculate_amounts(
                sqrt_price_lower, sqrt_price, sqrt_price_upper, wallet_amount0, None, None, decimals0, decimals1
            )
            transaction = TransactionHelperUniv3.handle_transaction(transaction, new_amount, new_amount0, new_amount1)
            if new_amount0 != wallet_amount0:
                raise ValueError("Amount0 should be equal to wallet_amount0")
            logging.warning(f"Adjusted amount0 and amount1 for transaction : , {asdict(transaction)}")

        elif amount0 <= wallet_amount0 and amount1 > wallet_amount1:
            new_amount, new_amount0, new_amount1 = calculate_amounts(
                sqrt_price_lower, sqrt_price, sqrt_price_upper, None, wallet_amount1, None, decimals0, decimals1
            )
            transaction = TransactionHelperUniv3.handle_transaction(transaction, new_amount, new_amount0, new_amount1)
            if new_amount1 != wallet_amount1:
                raise ValueError("Amount1 should be equal to wallet_amount1")
            logging.warning(f"Adjusted amount0 and amount1 for transaction : , {asdict(transaction)}")

        elif amount0 > wallet_amount0 and amount1 > wallet_amount1:
            first_test_amount, first_test_amount0, first_test_amount1 = calculate_amounts(
                sqrt_price_lower, sqrt_price, sqrt_price_upper, wallet_amount0, None, None, decimals0, decimals1
            )
            if first_test_amount0 <= wallet_amount0 and first_test_amount1 <= wallet_amount1:
                transaction = TransactionHelperUniv3.handle_transaction(
                    transaction, first_test_amount, first_test_amount0, first_test_amount1
                )
                logging.warning(f"Adjusted amount0 and amount1 for transaction : , {asdict(transaction)}")
                return transaction
            second_test_amount, second_test_amount0, second_test_amount1 = calculate_amounts(
                sqrt_price_lower, sqrt_price, sqrt_price_upper, None, wallet_amount1, None, decimals0, decimals1
            )
            if second_test_amount0 <= wallet_amount0 and second_test_amount1 <= wallet_amount1:
                transaction = TransactionHelperUniv3.handle_transaction(
                    transaction, second_test_amount, second_test_amount0, second_test_amount1
                )
                logging.warning(f"Adjusted amount0 and amount1 for transaction : , {asdict(transaction)}")
                return transaction
            raise ValueError("Amounts are not correct")
        else:
            transaction = TransactionHelperUniv3.handle_transaction(transaction, amount, amount0, amount1)

        return transaction

    @staticmethod
    def handle_transaction(
        transaction: MintTransactionUniv3, amount: int, amount0: int, amount1: int
    ) -> MintTransactionUniv3:
        flag = transaction.amount is not None
        flag0 = transaction.amount0 is not None
        flag1 = transaction.amount1 is not None
        if flag:
            transaction.amount = amount
            return transaction
        elif flag0:
            transaction.amount0 = amount0
            return transaction
        elif flag1:
            transaction.amount1 = amount1
            return transaction
        else:
            raise ValueError("No amount is provided")

    @staticmethod
    def create_mint_transaction(**kwargs) -> MintTransactionUniv3:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "amount": None,
            "amount0": None,
            "amount1": None,
            "tick_lower": -887272,
            "tick_upper": 887272,
            "token_id": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a MintTransaction object
        mint_transaction = MintTransactionUniv3(**fields)
        return mint_transaction

    @staticmethod
    def create_burn_transaction(**kwargs) -> BurnTransactionUniv3:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "amount": None,
            "amount0": None,
            "amount1": None,
            "tick_lower": -887272,
            "tick_upper": 887272,
            "token_id": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a BurnTransaction object
        burn_transaction = BurnTransactionUniv3(**fields)
        return burn_transaction

    @staticmethod
    def create_collect_transaction(**kwargs) -> CollectTransactionUniv3:
        # Set default values for all fields
        fields = {"block_number": None, "protocol_id": None, "sender_wallet": None, "token_id": None}
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a CollectTransaction object
        collect_transaction = CollectTransactionUniv3(**fields)
        return collect_transaction

    @staticmethod
    def create_swap_transaction(**kwargs) -> SwapTransactionUniv3:
        # Set default values for all fields
        fields = {
            "block_number": None,
            "protocol_id": None,
            "sender_wallet": None,
            "amount0_in": None,
            "amount1_in": None,
            "amount0_out": None,
            "amount1_out": None,
        }
        # Update the values based on provided keyword arguments
        fields.update(kwargs)
        # Create a SwapTransaction object
        swap_transaction = SwapTransactionUniv3(**fields)
        return swap_transaction

    @property
    def mapping_action_helper(self) -> dict[str, Callable[[dict], ABCTransaction]]:
        return {
            ParamsUniv3TransactionType.SWAP.value: self.create_swap_transaction,
            ParamsUniv3TransactionType.MINT.value: self.create_mint_transaction,
            ParamsUniv3TransactionType.BURN.value: self.create_burn_transaction,
            ParamsUniv3TransactionType.COLLECT.value: self.create_collect_transaction,
        }

    def convert_amounts_to_integers(self, transaction: TransactionUniv3, **kwargs: str) -> TransactionUniv3:
        # check that symbol0 and symbol1 are in the kwargs
        symbol0, symbol1, sqrt_price_x96 = kwargs.get("symbol0"), kwargs.get("symbol1"), kwargs.get("sqrt_price_x96")
        if symbol0 is None or symbol1 is None or sqrt_price_x96 is None:
            raise ValueError("symbol0 or symbol1 or sqrt_price_x96 is None")
        wallet = transaction.sender_wallet
        if wallet is None:
            raise ValueError("Wallet is None")

        decimals0 = wallet.tokens_metadata[symbol0].decimals
        decimals1 = wallet.tokens_metadata[symbol1].decimals
        if isinstance(transaction, SwapTransactionUniv3):
            transaction.amount0_in = (
                rescale_to_int(transaction.amount0_in, decimals0) if transaction.amount0_in is not None else None
            )
            transaction.amount1_in = (
                rescale_to_int(transaction.amount1_in, decimals1) if transaction.amount1_in is not None else None
            )
            transaction.amount0_out = (
                rescale_to_int(transaction.amount0_out, decimals0) if transaction.amount0_out is not None else None
            )
            transaction.amount1_out = (
                rescale_to_int(transaction.amount1_out, decimals1) if transaction.amount1_out is not None else None
            )
        elif isinstance(transaction, MintTransactionUniv3) or isinstance(transaction, BurnTransactionUniv3):
            transaction.amount = (
                rescale_to_int(transaction.amount, (decimals0 + decimals1) // 2)  # TODO how can we fix this in general?
                if transaction.amount is not None
                else None
            )
            transaction.amount0 = (
                rescale_to_int(transaction.amount0, decimals0) if transaction.amount0 is not None else None
            )
            transaction.amount1 = (
                rescale_to_int(transaction.amount1, decimals1) if transaction.amount1 is not None else None
            )

        if isinstance(transaction, MintTransactionUniv3) and ADJUST_MINT_AMOUNTS:
            transaction = TransactionHelperUniv3.adjust_mint_amounts(
                transaction,
                symbol0,
                symbol1,
                TickMath.sqrt_price_x96_to_sqrt_price(sqrt_price_x96, decimals0, decimals1),
            )
        return transaction


if __name__ == "__main__":
    """
    # swap 123 token0 for some token1
    swap = SwapTransaction(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        amount0=123,
        amount1=None
    )
    print(swap)
    # swap some token0 for 123 token1
    swap = SwapTransaction(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        amount0=None,
        amount1=-123 # negative!
    )
    print(swap)
    """
    # swap 123 token0 for some token1
    swap = SwapTransactionUniv3(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        amount0_in=123,
        amount1_in=None,
        amount0_out=None,
        amount1_out=None,
    )
    print(swap)
    # swap some token0 for 123 token1
    swap = SwapTransactionUniv3(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        amount0_in=None,
        amount1_in=None,
        amount0_out=None,
        amount1_out=123,
    )
    print(swap)
    mint = MintTransactionUniv3(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        tick_lower=-100,
        tick_upper=100,
        amount=123_000,
        amount0=None,
        amount1=None,
    )
    print(mint)
    burn = BurnTransactionUniv3(
        block_number=1,
        protocol_id="uniswap_v3",
        sender_wallet=None,
        tick_lower=-100,
        tick_upper=100,
        amount=123_000,
        amount0=None,
        amount1=None,
    )
    print(burn)
    collect = CollectTransactionUniv3(
        block_number=1, protocol_id="uniswap_v3", sender_wallet=None, tick_lower=-100, tick_upper=100
    )
    print(collect)
