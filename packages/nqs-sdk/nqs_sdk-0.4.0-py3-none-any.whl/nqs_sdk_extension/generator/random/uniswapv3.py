import logging
from decimal import Decimal
from typing import Any, Tuple

import numpy as np
from sortedcontainers import SortedKeyList

from nqs_sdk.utils.pickable_generator import PickableGenerator, StatefulGenerator
from nqs_sdk_extension.constants import MAX_SLIPPAGE, UNISWAPV3_RANDOM_AGENT_TICK_SPACING
from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.generator.random.random_transaction_generator import RandomTransactionGenerator
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.uniswap import (
    BurnTransactionUniv3,
    MintTransactionUniv3,
    ParamsUniv3TransactionType,
    SwapTransactionUniv3,
)

if USE_LEGACY_QIS:
    from nqs_sdk_extension.generator.random.random_transaction_generator import _send_transaction

TICK_MIN = -887272
TICK_MAX = 887272


class RandomUniv3Generator(RandomTransactionGenerator):
    def __init__(
        self,
        id: int,
        name: str,
        type: str,
        random_generation_parameters: dict,
        random_generator: RandomGenerator,
        mapping_block_timestamps: dict[int, int],
    ):
        super().__init__(id, name, type, random_generation_parameters, random_generator, mapping_block_timestamps)
        self._transaction_types = [
            transaction_type.value
            for transaction_type in ParamsUniv3TransactionType
            if transaction_type != ParamsUniv3TransactionType.COLLECT
        ]
        self.minted_positions: SortedKeyList[[int, MintTransactionUniv3]] = SortedKeyList(key=lambda x: x[0])
        self._observer: UniswapV3Observer
        self._tick_spacing: int = random_generation_parameters.get("mint", {}).get(
            "tick_spacing", UNISWAPV3_RANDOM_AGENT_TICK_SPACING
        )
        self.event_weights = self.get_event_weights(random_generation_parameters)
        self.unbounded_thr = self.get_unbounded_thr(random_generation_parameters)
        self._is_fitted_model: bool = True if len(self.event_weights) > 0 else False

    @staticmethod
    def get_event_weights(random_generation_parameters: dict) -> list[float]:
        if random_generation_parameters.get("event_probabilities", None) is None:
            return []
        else:
            event_proba = random_generation_parameters["event_probabilities"]
            weights = [event_proba["swap"], event_proba["mint"], 1 - (event_proba["swap"] + event_proba["mint"])]
            return weights

    @staticmethod
    def get_unbounded_thr(random_generation_parameters: dict) -> float:
        return float(
            random_generation_parameters.get("mint", {})
            .get("values", {})
            .get("is_unbounded", {})
            .get("uniform", {})
            .get("threshold", 0.0)
        )

    def validate_observer(self) -> None:
        if not isinstance(self._observer, UniswapV3Observer):
            raise ValueError("The observer is not of the correct type")
        return

    def sample_next_transaction_type(self) -> str:
        i = next(self.random_generator.process_dict["discrete"].draw_single(weights=self.event_weights))
        if i == 0:
            return ParamsUniv3TransactionType.SWAP.value
        elif i == 1:
            return ParamsUniv3TransactionType.MINT.value
        elif i == 2:
            return ParamsUniv3TransactionType.BURN.value
        else:
            raise ValueError

    @staticmethod
    def validate_tick_args(tick_args: dict[str, float | None]) -> None:
        if (tick_args["tick_lower"] is None) == (tick_args["relative_price_lower"] is None):
            raise ValueError("Exactly one of tick_lower and relative_price_lower must be provided")

        if (tick_args["tick_upper"] is None) == (tick_args["relative_price_upper"] is None):
            raise ValueError("Exactly one of tick_upper and relative_price_upper must be provided")

        if (tick_args["tick_lower"] is None) != (tick_args["tick_upper"] is None):
            raise ValueError("tick_upper must be provided if tick_lower is provided")

        if (tick_args["relative_price_lower"] is None) != (tick_args["relative_price_upper"] is None):
            raise ValueError("relative_price_upper must be provided if relative_price_lower is provided")

    def generate_mint_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float | list[float]]
    ) -> MintTransactionUniv3:
        if self._is_fitted_model:
            return self.generate_calibrated_mint_transactions_at_block(block_number, value_dict)
        else:
            return self.generate_random_mint_transactions_at_block(block_number, value_dict)  # type: ignore

    def generate_calibrated_mint_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float | list[float]]
    ) -> MintTransactionUniv3:
        unbounded_sample: float = value_dict["is_unbounded"]  # type: ignore
        marks: list[float] = value_dict["marks"]  # type: ignore
        is_unbounded = unbounded_sample < self.unbounded_thr
        amount = int(np.exp(marks[0]) * (10 ** ((self._observer.amm.decimals0 + self._observer.amm.decimals1) / 2)))

        if is_unbounded:
            tick_lower = TICK_MIN
            tick_upper = TICK_MAX
        else:
            price_spread = np.inf if is_unbounded else marks[1]
            price_rel = np.inf if is_unbounded else marks[2]

            dex_spot = list(self._observer._get_pool_dex_spot().values())[0].value / (
                10 ** list(self._observer._get_pool_dex_spot().values())[0].decimals
            )

            # price_spread = ( price_upper - price_lower ) /  dex_spot
            # price_rel = ( price_upper + price_lower ) / (2 * dex_spot)
            price_upper = dex_spot * (2 * price_rel + price_spread) / 2
            price_lower = dex_spot * (2 * price_rel - price_spread) / 2

            tick_lower = TickMath.price_to_tick(price_lower, self._observer.amm.decimals0, self._observer.amm.decimals1)
            tick_upper = TickMath.price_to_tick(price_upper, self._observer.amm.decimals0, self._observer.amm.decimals1)
        return self.create_mint_transactions_from_parameters(tick_upper, tick_lower, block_number, amount)

    def generate_random_mint_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float]
    ) -> MintTransactionUniv3:
        tick_args = {
            "tick_lower": value_dict.get("tick_lower", None),
            "tick_upper": value_dict.get("tick_upper", None),
            "relative_price_lower": value_dict.get("relative_price_lower", None),
            "relative_price_upper": value_dict.get("relative_price_upper", None),
        }

        self.validate_tick_args(tick_args)

        if tick_args["tick_lower"] is not None and tick_args["tick_upper"] is not None:
            tick_lower = tick_args["tick_lower"]
            tick_upper = tick_args["tick_upper"]
        elif tick_args["relative_price_lower"] is not None and tick_args["relative_price_upper"] is not None:
            price = list(self._observer._get_pool_dex_spot().values())[0].value / (
                10 ** list(self._observer._get_pool_dex_spot().values())[0].decimals
            )
            price_lower = max(tick_args["relative_price_lower"] * price, 0)
            price_upper = max(tick_args["relative_price_upper"] * price, 0)
            price_lower, price_upper = min(price_upper, price_lower), max(price_upper, price_lower)
            if price_lower == 0 and price_upper == 0:
                tick_lower = TICK_MIN
                tick_upper = TICK_MAX
            else:
                tick_lower = TickMath.price_to_tick(
                    price_lower, self._observer.amm.decimals0, self._observer.amm.decimals1
                )
                tick_upper = TickMath.price_to_tick(
                    price_upper, self._observer.amm.decimals0, self._observer.amm.decimals1
                )

        amount_args = {
            "amount": value_dict.get("amount", None),
            "pct_of_pool": value_dict.get("pct_of_pool", None),
        }

        if (amount_args["amount"] is None) == (amount_args["pct_of_pool"] is None):
            raise ValueError("Exactly one of amount and pct_of_pool must be provided")

        if amount_args["amount"] is not None:
            amount = int(
                amount_args["amount"] * (10 ** ((self._observer.amm.decimals0 + self._observer.amm.decimals1) / 2))
            )
        elif amount_args["pct_of_pool"] is not None:
            pool_liquidity = self._observer.amm.liquidity
            amount = int(amount_args["pct_of_pool"] * pool_liquidity)

        return self.create_mint_transactions_from_parameters(int(tick_upper), int(tick_lower), block_number, amount)

    def create_mint_transactions_from_parameters(
        self, tick_upper: int, tick_lower: int, block_number: int, amount: int
    ) -> MintTransactionUniv3:
        tick_lower = (
            tick_lower
            if tick_lower % self._tick_spacing == 0
            else max((tick_lower // self._tick_spacing + 1) * self._tick_spacing, TICK_MIN)
        )
        tick_upper = (
            tick_upper
            if tick_upper % self._tick_spacing == 0
            else min((tick_upper // self._tick_spacing + 1) * self._tick_spacing, TICK_MAX)
        )

        if tick_lower > tick_upper:
            tick_lower, tick_upper = tick_upper, tick_lower

        elif tick_upper == tick_lower:
            tick_lower = tick_upper - self._tick_spacing

        mint_transaction = MintTransactionUniv3(
            block_number=block_number,
            protocol_id=self._protocol_id,
            sender_wallet=None,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount=amount,
        )
        self.minted_positions.add((block_number, mint_transaction))
        return mint_transaction

    def generate_burn_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float]
    ) -> BurnTransactionUniv3:
        max_index = self.minted_positions.bisect_key_right(block_number)
        if max_index == 0:
            logging.debug(
                f"Protocol: {self._protocol_id}, Block Number: {block_number}, No minted positions left to burn"
            )
            return BurnTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                tick_lower=-887272,
                tick_upper=887272,
                amount=0,
            )
        else:
            burn_position_id = next(
                self.random_generator.process_dict["uniform_discrete"].draw_single(bounds=(0, max_index))
            )
            block, minted_position = self.minted_positions.pop(burn_position_id)
            return BurnTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                tick_lower=minted_position.tick_lower,
                tick_upper=minted_position.tick_upper,
                amount=minted_position.amount,
            )

    def generate_swap_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float]
    ) -> SwapTransactionUniv3:
        if self._is_fitted_model:
            return self.generate_calibrated_swap_transactions_at_block(block_number, value_dict)
        else:
            return self.generate_random_swap_transactions_at_block(block_number, value_dict)

    def generate_calibrated_swap_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float]
    ) -> SwapTransactionUniv3:
        token0_to_token1 = value_dict["mark"] > 0
        token_amount = abs(value_dict["mark"])
        decimals_token_in = self._observer.amm.decimals0 if token0_to_token1 else self._observer.amm.decimals1

        # fixme for the moment the calibrated distribution assumes that amounts are expressed in USD.
        #  Thibault says this can be changed on his code - the alternative would be to write the correct amounts in the
        #  broker as the spot oracle should not be queried at this stage
        token_amount = 10

        if token0_to_token1:
            return SwapTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                amount0_in=int(Decimal(token_amount).scaleb(decimals_token_in)),
                amount1_in=None,
                sqrt_price_limit_x96=None,
            )
        else:
            return SwapTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                amount0_in=None,
                amount1_in=int(Decimal(token_amount).scaleb(decimals_token_in)),
                sqrt_price_limit_x96=None,
            )

    def generate_random_swap_transactions_at_block(
        self, block_number: int, value_dict: dict[str, float]
    ) -> SwapTransactionUniv3:
        pool_liquidity = self._observer.amm.liquidity * self._observer.amm.factor_liquidity
        dex_spot = (
            list(self._observer._get_pool_dex_spot().values())[0].value
            / 10 ** list(self._observer._get_pool_dex_spot().values())[0].decimals
        )
        sqrt_dex_spot = np.sqrt(dex_spot)

        amount_args = {
            "pct_of_pool": value_dict.get("pct_of_pool", None),
            "amount_token0": value_dict.get("amount_token0", None),
            "amount_token1": value_dict.get("amount_token1", None),
        }

        if (amount_args["pct_of_pool"] is None) == (
            amount_args["amount_token0"] is None or amount_args["amount_token1"] is None
        ):
            raise ValueError("Either pct_of_pool or both amount_token0 and amount_token1 must be provided")

        if amount_args["pct_of_pool"] is not None:
            amount = amount_args["pct_of_pool"] * pool_liquidity
            amount0 = int((amount / sqrt_dex_spot) * (10**self._observer.amm.decimals0))
            amount1 = int(amount * sqrt_dex_spot * (10**self._observer.amm.decimals1))
        else:
            amount0 = amount_args["amount_token0"] * (10**self._observer.amm.decimals0)
            amount1 = amount_args["amount_token1"] * (10**self._observer.amm.decimals1)

        if value_dict["token_in"] == 0:
            return SwapTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                amount0_in=amount0,
                amount1_in=None,
                sqrt_price_limit_x96=None
                if MAX_SLIPPAGE is None
                else TickMath.price_to_sqrt_price_x96(
                    dex_spot * (1 - MAX_SLIPPAGE), self._observer.amm.decimals0, self._observer.amm.decimals1
                ),
            )
        else:
            return SwapTransactionUniv3(
                block_number=block_number,
                protocol_id=self._protocol_id,
                sender_wallet=None,
                amount0_in=None,
                amount1_in=amount1,
                sqrt_price_limit_x96=None
                if MAX_SLIPPAGE is None
                else TickMath.price_to_sqrt_price_x96(
                    dex_spot * (1 + MAX_SLIPPAGE), self._observer.amm.decimals0, self._observer.amm.decimals1
                ),
            )

    @property
    def transaction_types(self) -> list[str]:
        return self._transaction_types

    def generate_transaction_at_block(self, transaction_type: str, **kwargs: Any) -> ABCTransaction:
        match transaction_type:
            case ParamsUniv3TransactionType.MINT.value:
                return self.generate_mint_transactions_at_block(**kwargs)
            case ParamsUniv3TransactionType.BURN.value:
                return self.generate_burn_transactions_at_block(**kwargs)
            case ParamsUniv3TransactionType.SWAP.value:
                return self.generate_swap_transactions_at_block(**kwargs)
            case _:
                raise ValueError(f"Invalid transaction type: {transaction_type}")

    if USE_LEGACY_QIS:

        def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
            """
            Sends the next generated transaction to the message dispatcher.

            Args:
                **kwargs (Any): Additional keyword arguments.

            Yields:
                Generator: The generated transactions.

            """
            # here the condition should check if we are under a "calibrated generator"
            if not self._is_fitted_model:
                return super().produce_next_message(**kwargs)

            block_number_from = kwargs["block_number_from"]
            block_number_to = kwargs["block_number_to"]
            total_block_number = block_number_to - block_number_from
            frequency_params_per_transaction_type = self.get_frequency_params_per_transaction_type(
                self.random_generation_parameters
            )
            pending_transactions_by_block: dict[int, list[ABCTransaction]] = {}
            pending_trx_types: list[str] = []

            def update(
                state: Tuple[RandomUniv3Generator, int, dict[int, list[ABCTransaction]], list[str]],
            ) -> Tuple[Tuple[RandomUniv3Generator, int, dict[int, list[ABCTransaction]], list[str]], None]:
                (
                    transaction_generator,
                    current_block_number,
                    pending_transactions_by_block,
                    pending_trx_types,
                ) = state
                # iterate over all blocks
                while current_block_number < block_number_to:
                    # generate transactions till we have one transaction per type
                    next_transaction_block = (
                        max(pending_transactions_by_block.keys())
                        if len(pending_transactions_by_block) > 0
                        else current_block_number
                    )
                    while (
                        len(set(pending_trx_types)) < len(transaction_generator.transaction_types)
                        and next_transaction_block < block_number_to
                    ):
                        transaction_type = transaction_generator.sample_next_transaction_type()

                        frequency_process, frequency_params = frequency_params_per_transaction_type[transaction_type]
                        # add current timestamp in case seasonality is taken into account
                        current_timestamp = self.mapping_block_timestamps[current_block_number]
                        frequency_params.update({"timestamp": current_timestamp})
                        number_of_blocks_until_next_transaction = self.generate_next_transaction_time(
                            frequency_process, frequency_params, total_block_number
                        )

                        next_transaction_block += number_of_blocks_until_next_transaction
                        # if the next transaction block is after the last block, we need to stop
                        if next_transaction_block > block_number_to:
                            break

                        pending_transactions_by_block = self.generate_transaction(
                            next_transaction_block,
                            transaction_type,
                            pending_transactions_by_block,
                        )
                        pending_trx_types += [transaction_type]

                    current_block_number = min(pending_transactions_by_block.keys())
                    if current_block_number == block_number_to or next_transaction_block >= block_number_to:
                        # if we are at the last block, we need to send the remaining transactions
                        while len(pending_trx_types) > 0:
                            pending_transactions_by_block, _ = _send_transaction(
                                transaction_generator, pending_transactions_by_block
                            )
                            # drop the first transaction as it has been sent
                            pending_trx_types = pending_trx_types[1:]
                        return (
                            transaction_generator,
                            block_number_to,
                            pending_transactions_by_block,
                            pending_trx_types,
                        ), None

                    else:
                        pending_transactions_by_block, _ = _send_transaction(
                            transaction_generator, pending_transactions_by_block
                        )
                        pending_trx_types = pending_trx_types[1:]
                        return (
                            transaction_generator,
                            current_block_number,
                            pending_transactions_by_block,
                            pending_trx_types,
                        ), None

                raise StopIteration

            return StatefulGenerator(
                (
                    self,
                    block_number_from,
                    pending_transactions_by_block,
                    pending_trx_types,
                ),
                update,
            )

    def generate_transaction(
        self,
        next_transaction_block: int,
        transaction_type: str,
        pending_transactions_by_block: dict[int, list[ABCTransaction]],
    ) -> dict[int, list[ABCTransaction]]:
        """
        Generate a transaction and store it in the pending transactions by block dictionary.
        """
        transaction = self.generate_transactions_at_block_by_type(next_transaction_block, transaction_type)
        pending_transactions_by_block.setdefault(next_transaction_block, []).append(transaction)
        return pending_transactions_by_block
