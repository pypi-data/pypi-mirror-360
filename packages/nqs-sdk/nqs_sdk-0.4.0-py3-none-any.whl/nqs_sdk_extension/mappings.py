import logging
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Tuple

from nqs_pycore import Wallet

from nqs_sdk_extension.generator.random.compoundv2 import RandomCompoundv2Generator
from nqs_sdk_extension.generator.random.random_transaction_generator import RandomTransactionGenerator
from nqs_sdk_extension.generator.random.uniswapv3 import RandomUniv3Generator
from nqs_sdk_extension.observer.protocol.cex import CEXObserver
from nqs_sdk_extension.observer.protocol.compoundv2 import ComptrollerObserver
from nqs_sdk_extension.observer.protocol.protocol_observer import ProtocolObserver
from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk_extension.protocol.cex import CEX
from nqs_sdk_extension.protocol.lending_protocol.compoundv2.compoundv2 import Comptroller
from nqs_sdk_extension.run_configuration.protocol_parameters.cex import CEXProtocolInformation
from nqs_sdk_extension.run_configuration.protocol_parameters.compoundv2 import Compoundv2ProtocolInformation
from nqs_sdk_extension.run_configuration.protocol_parameters.protocol import SimulatedProtocolInformation
from nqs_sdk_extension.run_configuration.protocol_parameters.uniswapv3 import Uniswapv3ProtocolInformation
from nqs_sdk_extension.transaction.cex import TransactionHelperCEX
from nqs_sdk_extension.transaction.compoundv2 import TransactionHelperCompoundv2
from nqs_sdk_extension.transaction.transaction_helper import ProtocolTransactionHelper
from nqs_sdk_extension.transaction.uniswap import TransactionHelperUniv3
from nqs_sdk_extension.wallet import MissingERC721Error


class ProtocolTypes(Enum):
    """Enum to represent the different types of protocols that can be simulated."""

    COMPOUND_V2 = "compound_v2"
    UNISWAP_V3 = "uniswap_v3"
    CEX = "cex"


mapping_type_to_protocol_info: dict[str, type[SimulatedProtocolInformation]] = {
    ProtocolTypes.COMPOUND_V2.value: Compoundv2ProtocolInformation,
    ProtocolTypes.UNISWAP_V3.value: Uniswapv3ProtocolInformation,
    ProtocolTypes.CEX.value: CEXProtocolInformation,
}

mapping_type_to_generator: dict[str, Optional[type[RandomTransactionGenerator]]] = {
    ProtocolTypes.COMPOUND_V2.value: RandomCompoundv2Generator,
    ProtocolTypes.UNISWAP_V3.value: RandomUniv3Generator,
}

mapping_type_to_protocol: dict[str, type[ABCProtocol]] = {
    ProtocolTypes.COMPOUND_V2.value: Comptroller,
    ProtocolTypes.UNISWAP_V3.value: UniswapV3,
    ProtocolTypes.CEX.value: CEX,
}

mapping_protocol_to_type: dict[type[ABCProtocol], str] = {
    Comptroller: ProtocolTypes.COMPOUND_V2.value,
    UniswapV3: ProtocolTypes.UNISWAP_V3.value,
    CEX: ProtocolTypes.CEX.value,
}

mapping_type_to_observer: dict[str, type[ProtocolObserver]] = {
    ProtocolTypes.COMPOUND_V2.value: ComptrollerObserver,
    ProtocolTypes.UNISWAP_V3.value: UniswapV3Observer,
    ProtocolTypes.CEX.value: CEXObserver,
}

mapping_type_to_protocol_transaction_helper: dict[str, type[ProtocolTransactionHelper]] = {
    ProtocolTypes.COMPOUND_V2.value: TransactionHelperCompoundv2,
    ProtocolTypes.UNISWAP_V3.value: TransactionHelperUniv3,
    ProtocolTypes.CEX.value: TransactionHelperCEX,
}

NUMERICAL_ARGS_COMPOUNDV2 = {
    "mint_amount",
    "redeem_amount_in",
    "redeem_tokens_in",
    "borrow_amount",
    "repay_amount",
    "amount",
}
NUMERICAL_ARGS_UNIV3 = {
    "tick_lower",
    "tick_upper",
    "price_lower",
    "price_upper",
    "amount",
    "amount0",
    "amount1",
    "amount0_in",
    "amount1_in",
    "amount0_out",
    "amount1_out",
    "amount_sold",
}

NUMERICAL_ARGS_CEX = {"amount_to_sell", "amount_to_buy"}

ALLOWED_NUMERICAL_ARGS = set.union(NUMERICAL_ARGS_COMPOUNDV2, NUMERICAL_ARGS_UNIV3, NUMERICAL_ARGS_CEX)


class ConversionMethodsUniv3:
    @staticmethod
    def check_token_id_tick_range_consistency(**kwargs: Any) -> list:
        tick_lower: int | None = kwargs.get("tick_lower", None)
        tick_upper: int | None = kwargs.get("tick_upper", None)
        price_lower: float | None = kwargs.get("price_lower", None)
        price_upper: float | None = kwargs.get("price_upper", None)
        wallet: Wallet = kwargs["sender_wallet"]
        token_id: str = kwargs["token_id"]
        pool: UniswapV3 = kwargs["protocol"]

        if tick_lower is None and tick_upper is None and price_lower is not None and price_upper is not None:
            new_tick_lower = TickMath.price_to_tick(float(price_lower), pool.decimals0, pool.decimals1)
            new_tick_upper = TickMath.price_to_tick(float(price_upper), pool.decimals0, pool.decimals1)
        elif tick_lower is not None and tick_upper is not None and price_lower is None and price_upper is None:
            new_tick_lower = tick_lower
            new_tick_upper = tick_upper
        elif tick_lower is None and tick_upper is None and price_lower is None and price_upper is None:
            new_tick_lower = None
            new_tick_upper = None
        elif tick_lower is not None and tick_upper is None and price_lower is None and price_upper is not None:
            new_tick_lower = tick_lower
            new_tick_upper = TickMath.price_to_tick(float(price_upper), pool.decimals0, pool.decimals1)
        elif tick_lower is None and tick_upper is not None and price_lower is not None and price_upper is None:
            new_tick_lower = TickMath.price_to_tick(float(price_lower), pool.decimals0, pool.decimals1)
            new_tick_upper = tick_upper

        try:
            position_tick_lower, position_tick_upper = wallet.get_token_id_tick_range(
                token_id, kwargs.get("action_name")
            )
            # if the tick range of the existing position differs from the tick range specified in the parameters
            # we raise an error. (if no tick range is specified in the parameters, we allow to add to the existing
            # position)
            if (position_tick_lower != new_tick_lower or position_tick_upper != new_tick_upper) and (
                tick_lower is not None or tick_upper is not None or price_lower is not None or price_upper is not None
            ):
                new_token_id = wallet.get_next_token_id(token_id, pool.name)
                message = (
                    f"Trying to mint on position ID {token_id} on the range {new_tick_lower}-{new_tick_upper}, "
                    f"but such position ID already exists with the range "
                    f"{position_tick_lower}-{position_tick_upper}"
                    f"Creating a new ID for the new position : {new_token_id}"
                )
                logging.warning(message)
                return [new_tick_lower, new_tick_upper, new_token_id]
        except Exception:
            if new_tick_lower is None or new_tick_upper is None:
                position_tick_lower, position_tick_upper = TickMath.MIN_TICK, TickMath.MAX_TICK
            else:
                position_tick_lower, position_tick_upper = new_tick_lower, new_tick_upper
        return [position_tick_lower, position_tick_upper, token_id]

    @staticmethod
    def amount_ratio_to_amount(**kwargs: Any) -> list:
        tick_lower: int | None = kwargs.get("tick_lower", None)
        tick_upper: int | None = kwargs.get("tick_upper", None)
        price_lower: float | None = kwargs.get("price_lower", None)
        price_upper: float | None = kwargs.get("price_upper", None)
        wallet: Wallet = kwargs["sender_wallet"]
        pool: UniswapV3 = kwargs["protocol"]
        amount_ratio: float = kwargs["amount_ratio"]
        position_id: str | None = kwargs.get("token_id", None)

        if position_id is not None:
            token = wallet.get_erc721_token(position_id)
            return [Decimal(token.liquidity).scaleb(int(-pool.liquidity_decimals)) * Decimal(amount_ratio)]

        if price_lower is not None:
            tick_lower = ConversionMethodsUniv3.price_lower_to_tick_lower(
                price_lower, pool.decimals0, pool.decimals1, position_id
            )
        if price_upper is not None:
            tick_upper = TickMath.price_to_tick(float(price_upper), pool.decimals0, pool.decimals1)

        positions = wallet.get_erc721_tokens_for_pool_name(pool.name)
        for position in positions:
            if position.tick_lower == tick_lower and position.tick_upper == tick_upper:
                return [Decimal(position.liquidity).scaleb(int(-pool.liquidity_decimals)) * Decimal(amount_ratio)]

        raise ValueError(f"Position with tick range {tick_lower}-{tick_upper} not found in wallet")

    @staticmethod
    def translate_swap_amounts(**kwargs: Any) -> list:
        token_to_sell: str = kwargs["token_to_sell"]
        amount: Decimal = Decimal(kwargs["amount_sold"])
        pool: UniswapV3 = kwargs["protocol"]
        if token_to_sell == pool.symbol0:
            return [amount, None]
        elif token_to_sell == pool.symbol1:
            return [None, amount]
        else:
            raise ValueError(f"Token {token_to_sell} is not in the pool {pool.symbol0}/{pool.symbol1}")

    @staticmethod
    def get_token_tick_range_or_none(**kwargs: Any) -> Any:
        try:
            tick_range = kwargs["sender_wallet"].get_token_id_tick_range(
                kwargs["token_id"], kwargs.get("action_name")
            ) + [kwargs["token_id"]]
            return tick_range
        except MissingERC721Error:
            return [TickMath.MIN_TICK, TickMath.MAX_TICK, kwargs["token_id"]]

    @staticmethod
    def price_lower_to_tick_lower(
        price_lower: float, decimals0: int, decimals1: int, position_id: Optional[str] = None
    ) -> int:
        if price_lower == 0:
            if position_id is not None:
                logging.warning(f"Position {position_id} has a price_lower of 0. Tick lower set to min tick instead.")
            return TickMath.MIN_TICK
        return TickMath.price_to_tick(float(price_lower), decimals0, decimals1)


action_conversion_dictionary: dict[Tuple[str, str, str], dict[str, Any]]
action_conversion_dictionary = {
    ("uniswap_v3", "mint", "price_lower"): {
        "field": ["tick_lower"],
        "conversion_method": lambda **kwargs: [
            ConversionMethodsUniv3.price_lower_to_tick_lower(
                float(kwargs["price_lower"]), kwargs["protocol"].decimals0, kwargs["protocol"].decimals1
            )
        ],
    },
    ("uniswap_v3", "mint", "price_upper"): {
        "field": ["tick_upper"],
        "conversion_method": lambda **kwargs: [
            TickMath.price_to_tick(
                float(kwargs["price_upper"]), kwargs["protocol"].decimals0, kwargs["protocol"].decimals1
            )
        ],
    },
    ("uniswap_v3", "burn", "price_lower"): {
        "field": ["tick_lower"],
        "conversion_method": lambda **kwargs: [
            TickMath.price_to_tick(
                float(kwargs["price_lower"]), kwargs["protocol"].decimals0, kwargs["protocol"].decimals1
            )
        ],
    },
    ("uniswap_v3", "burn", "price_upper"): {
        "field": ["tick_upper"],
        "conversion_method": lambda **kwargs: [
            TickMath.price_to_tick(
                float(kwargs["price_upper"]), kwargs["protocol"].decimals0, kwargs["protocol"].decimals1
            )
        ],
    },
    ("uniswap_v3", "burn", "token_id"): {
        "field": ["tick_lower", "tick_upper", "token_id"],
        "conversion_method": ConversionMethodsUniv3.get_token_tick_range_or_none,
    },
    ("uniswap_v3", "collect", "token_id"): {
        "field": ["tick_lower", "tick_upper", "token_id"],
        "conversion_method": ConversionMethodsUniv3.get_token_tick_range_or_none,
    },
    ("uniswap_v3", "mint", "token_id"): {
        "field": ["tick_lower", "tick_upper", "token_id"],
        "conversion_method": ConversionMethodsUniv3.check_token_id_tick_range_consistency,
    },
    ("uniswap_v3", "burn", "amount_ratio"): {
        "field": ["amount"],
        "conversion_method": ConversionMethodsUniv3.amount_ratio_to_amount,
    },
    ("uniswap_v3", "swap", "token_to_sell"): {
        "field": ["amount0_in", "amount1_in"],
        "conversion_method": ConversionMethodsUniv3.translate_swap_amounts,
    },
    ("uniswap_v3", "swap", "amount_sold"): {
        "field": [],
        "conversion_method": lambda **kwargs: kwargs,
    },
    ("compound_v2", "mint", "market"): {
        "field": ["ctoken"],
        "conversion_method": lambda **kwargs: ["c" + kwargs["market"]],
    },
    ("compound_v2", "borrow", "market"): {
        "field": ["ctoken"],
        "conversion_method": lambda **kwargs: ["c" + kwargs["market"]],
    },
    ("compound_v2", "redeem", "market"): {
        "field": ["ctoken"],
        "conversion_method": lambda **kwargs: ["c" + kwargs["market"]],
    },
    ("compound_v2", "repay", "market"): {
        "field": ["ctoken"],
        "conversion_method": lambda **kwargs: ["c" + kwargs["market"]],
    },
}
ux_fields = list(action_conversion_dictionary.keys())
