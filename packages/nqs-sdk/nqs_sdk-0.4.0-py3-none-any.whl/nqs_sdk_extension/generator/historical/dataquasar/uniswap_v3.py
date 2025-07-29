import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np
from sortedcontainers import SortedDict

from nqs_sdk import BlockNumberOrTimestamp
from nqs_sdk_extension.generator.historical.dataquasar.abc_dtq import DTQSoloGenerator
from nqs_sdk_extension.spot import DataLoader
from nqs_sdk_extension.state import ABCProtocolState, StateUniv3, TickDataUniv3
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.uniswap import BurnTransactionUniv3, MintTransactionUniv3, SwapTransactionUniv3


class PoolCallName(Enum):
    MINT = "Mint"
    BURN = "Burn"
    SWAP = "Swap"
    COLLECT = "Collect"


class DTQUniswapV3Generator(DTQSoloGenerator):
    def __init__(self, id: int, name: str, protocol_info: dict):
        super().__init__(id, name)
        self.pool_address = protocol_info["address"]
        pool_data = DataLoader.quantlib_source().uniswap_v3_pool_info(self.pool_address)
        if pool_data is None:
            raise ValueError(f"Pool {self.pool_address} not found")
        self.token0 = pool_data["token0"]
        self.token1 = pool_data["token1"]
        self.symbol0 = pool_data["token0_symbol"]
        self.symbol1 = pool_data["token1_symbol"]
        self.decimals0 = pool_data["token0_decimals"]
        self.decimals1 = pool_data["token1_decimals"]
        self.fee_tier = int(pool_data["fee_tier"].scaleb(4))  # in hundredth of a basis point
        self.tick_spacing = pool_data["tick_spacing"]
        # recurring computations
        self.factor = 10 ** ((self.decimals0 + self.decimals1) / 2)  # to map float to int
        self.factor0 = 10**self.decimals0
        self.factor1 = 10**self.decimals1
        # to be cleaned
        self._protocol_id = ""
        # logger
        self.logger = logging.getLogger("DTQUniswapV3GeneratorLogger")

    def generate_state_at_block(self, block_number: int) -> StateUniv3:
        # timestamp_str = self._block_to_formatted_datetime(block_number)
        timestamp = self._block_to_datetime(block_number)
        tick, sqrt_price_x96 = self._get_tick_and_sqrt_price_x96_at_block(block_number)
        data_lp = self._load_liquidity_positions(timestamp)
        ticks = self._make_ticks_from_liquidity_positions(data_lp)
        liquidity = self._compute_liquidity_from_liquidity_positions(tick, data_lp)
        state = StateUniv3(
            id=self.id,
            name=self.name,
            block_number=block_number,
            block_timestamp=timestamp,
            token0=self.token0,
            token1=self.token1,
            symbol0=self.symbol0,
            symbol1=self.symbol1,
            decimals0=self.decimals0,
            decimals1=self.decimals1,
            fee_tier=self.fee_tier,
            liquidity=liquidity,
            sqrt_price_x96=sqrt_price_x96,
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=tick,
            ticks=ticks,
        )
        return state

    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        return self.generate_transactions_between_blocks(block_number, block_number)

    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        data_calls = self._load_historical_calls(block_number_from, block_number_to)
        transactions = self._make_transaction_from_calls(data_calls)
        transactions.sort(key=lambda x: (x.block_number, x.block_index))
        self.logger.debug(
            f"Generated {len(transactions)} transactions between blocks {block_number_from} and {block_number_to}"
        )
        return transactions

    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        if not isinstance(state_left, StateUniv3) or not isinstance(state_right, StateUniv3):
            raise ValueError("States are not of type StateUniv3")
        self.logger.info(
            f"Comparing the current price: {(float(state_left.sqrt_price_x96) / 2 ** 96) ** 2:.4f} "
            f"vs {(float(state_right.sqrt_price_x96) / 2 ** 96) ** 2:.4f}"
        )
        self.logger.info(f"Comparing the current tick: {state_left.tick} vs {state_right.tick}")
        self.logger.info(
            f"Comparing the current liquidity: {state_left.liquidity / self.factor:.4e} "
            f"vs {state_right.liquidity / self.factor:.4e}"
        )
        self.logger.info(
            "Comparing the number of ticks: {} vs {}".format(len(state_left.ticks), len(state_right.ticks))
        )
        tickset_left, ticks_left = self._prepare_ticks_for_comparison(state_left.ticks)
        tickset_right, ticks_right = self._prepare_ticks_for_comparison(state_right.ticks)
        tickdiff = tickset_left.symmetric_difference(tickset_right)
        # ad-hoc threeshold for comparison, not smart
        threshold = int((state_left.sqrt_price_x96 / 2**96) ** 2 * self.factor - 1e-4)
        self.logger.debug(f"Threshold for liquidity comparison: {threshold}")
        if len(tickdiff) > 0:
            self.logger.info(f"Non-overlapping ticks: {tickdiff}")
            for t in tickdiff:
                if t in tickset_left:
                    tick = ticks_left[t]
                    side = "left"
                elif t in tickset_right:
                    tick = ticks_right[t]
                    side = "right"
                else:
                    raise ValueError("This should never happen")
                flag = "negligible" if abs(tick.liquidity_net) < threshold else "not negligible"
                self.logger.info(
                    f"Tick only in state {side}: tick={int(tick.tick_idx)}, "
                    f"net={tick.liquidity_net} ({flag}), gross={tick.liquidity_gross}"
                )
        tickinter = tickset_left.intersection(tickset_right)
        for t in tickinter:
            t = int(t)
            tick_left = ticks_left[t]
            tick_right = ticks_right[t]
            if tick_left.liquidity_net != tick_right.liquidity_net:
                delta_net = tick_left.liquidity_net - tick_right.liquidity_net
                flag = "negligible" if abs(delta_net) < threshold else "not negligible"
                self.logger.info(f"Tick {t} has different net liquidity: {delta_net} ({flag})")
            if tick_left.liquidity_gross != tick_right.liquidity_gross:
                delta_gross = tick_left.liquidity_gross - tick_right.liquidity_gross
                flag = "negligible" if abs(delta_gross) < threshold else "not negligible"
                self.logger.info(f"Tick {t} has different gross liquidity: {delta_gross} ({flag})")

    ##------------------------------------------------------------
    ## Private methods
    ##------------------------------------------------------------

    def _prepare_ticks_for_comparison(self, ticks: List[TickDataUniv3]) -> Tuple[set[int], dict[int, TickDataUniv3]]:
        self.ticks = {}
        for tick in ticks:
            self.ticks[tick.tick_idx] = tick
        self.tickSet = set(self.ticks.keys())
        return self.tickSet, self.ticks

    def _get_tick_and_sqrt_price_x96_at_block(self, block_number: int) -> Tuple[int, int]:
        bn = BlockNumberOrTimestamp.block_number(block_number)
        result = DataLoader.quantlib_source().uniswap_v3_pool_slot0_data(self.pool_address, bn)
        tick = result["tick"]
        sqrt_price_ratio_x96 = result["sqrt_price_ratio_x96"]
        return tick, sqrt_price_ratio_x96

    def _block_to_formatted_datetime(self, block_number: int) -> str:
        date = self._block_to_datetime(block_number)
        np_date = np.datetime64(datetime.utcfromtimestamp(date))
        formatted_date = np.datetime_as_string(np_date, timezone="UTC")
        return formatted_date

    def _block_to_datetime(self, block_number: int) -> int:
        bn1 = BlockNumberOrTimestamp.block_number(block_number)
        data = DataLoader.quantlib_source().blocks_from_interval("Ethereum", bn1, bn1)

        if len(data["timestamp"]) == 0:
            raise ValueError(f"No block found for block number {block_number} and pool {self.pool_address}")
        date = data["timestamp"][0]

        return date  # type: ignore

    def _load_liquidity_positions(self, timestamp: int) -> Dict:
        dt = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        data = DataLoader.quantlib_source().uniswap_v3_pool_liquidity_positions(
            contract_address=self.pool_address, timestamp=dt
        )
        return data

    def _load_historical_calls(self, begin: int, end: int) -> dict:
        formatted_begin = BlockNumberOrTimestamp.block_number(begin)
        formatted_end = BlockNumberOrTimestamp.block_number(end)
        data = DataLoader.quantlib_source().uniswap_v3_pool_calls(
            contract=self.pool_address, begin=formatted_begin, end=formatted_end
        )
        return data

    def _make_transaction_from_calls(self, data_calls: dict) -> list[ABCTransaction]:
        timestamp_vec = data_calls["timestamp"]
        block_number_vec = data_calls["block_number"]
        trace_index_vec = data_calls["trace_index"]
        call_name_vec = data_calls["call_name"]
        data_vec = data_calls["data"]
        transactions: list[ABCTransaction] = []
        for i in range(len(timestamp_vec)):
            match call_name_vec[i]:
                case PoolCallName.MINT.value:
                    transactions.append(
                        self._make_mint_transaction_from_call_data(data_vec[i], block_number_vec[i], trace_index_vec[i])
                    )
                case PoolCallName.BURN.value:
                    transactions.append(
                        self._make_burn_transaction_from_call_data(data_vec[i], block_number_vec[i], trace_index_vec[i])
                    )
                case PoolCallName.SWAP.value:
                    transactions.append(
                        self._make_swap_transaction_from_call_data(data_vec[i], block_number_vec[i], trace_index_vec[i])
                    )
                case PoolCallName.COLLECT.value:
                    pass
                case _:
                    raise ValueError(f"Unknown call name: {call_name_vec[i]}")
                    # self.logger.warning(f"Unknown call name: {call_name_vec[i]}")
        return transactions

    def _make_mint_transaction_from_call_data(self, data: dict, block_number: int, index: int) -> MintTransactionUniv3:
        return MintTransactionUniv3(
            sender_wallet=None,
            protocol_id=self._protocol_id,
            block_number=block_number,
            block_index=index,
            tick_lower=int(data["tickLower"]),
            tick_upper=int(data["tickUpper"]),
            amount=int(data["amount"]),
            # amount0 = int(data["output_amount0"]),
            # amount1 = int(data["output_amount1"]),
            amount0=None,
            amount1=None,
        )

    def _make_burn_transaction_from_call_data(self, data: dict, block_number: int, index: int) -> BurnTransactionUniv3:
        return BurnTransactionUniv3(
            sender_wallet=None,
            protocol_id=self._protocol_id,
            block_number=block_number,
            block_index=index,
            tick_lower=int(data["tickLower"]),
            tick_upper=int(data["tickUpper"]),
            amount=int(data["amount"]),
            # amount0 = int(data["output_amount0"]),
            # amount1 = int(data["output_amount1"]),
            amount0=None,
            amount1=None,
        )

    def _make_swap_transaction_from_call_data(self, data: dict, block_number: int, index: int) -> SwapTransactionUniv3:
        amount_specified = int(data["amountSpecified"])
        zero_for_one = bool(data["zeroForOne"])
        amount0_in: int | None = None
        amount1_in: int | None = None
        amount0_out: int | None = None
        amount1_out: int | None = None
        if amount_specified > 0:
            # swap exact input
            if zero_for_one:
                amount0_in = abs(amount_specified)
            else:
                amount1_in = abs(amount_specified)
        else:
            # swap exact output
            if zero_for_one:
                amount1_out = abs(amount_specified)
            else:
                amount0_out = abs(amount_specified)

        return SwapTransactionUniv3(
            sender_wallet=None,
            protocol_id=self._protocol_id,
            block_number=block_number,
            block_index=index,
            amount0_in=amount0_in,
            amount1_in=amount1_in,
            amount0_out=amount0_out,
            amount1_out=amount1_out,
            sqrt_price_limit_x96=int(data["sqrtPriceLimitX96"]),
        )

    def _make_ticks_from_liquidity_positions(self, data_lps: dict) -> List[TickDataUniv3]:
        tick_lower_vec = data_lps["tick_lower"]
        tick_upper_vec = data_lps["tick_upper"]
        lp_amount_vec = data_lps["lp_amount"]
        # assert len(tick_lower_vec) == len(tick_upper_vec) == len(lp_amount_vec)
        ticks_map = SortedDict()
        for i in range(len(tick_lower_vec)):
            # prepare data
            tick_lower = int(tick_lower_vec[i])
            tick_upper = int(tick_upper_vec[i])
            liquidity = int(Decimal(lp_amount_vec[i]) * Decimal(self.factor))
            # update lower tick
            tick_data_lower: TickDataUniv3 = ticks_map.get(tick_lower, None)
            if tick_data_lower is None:
                ticks_map[tick_lower] = TickDataUniv3(
                    tick_idx=int(tick_lower),
                    liquidity_net=liquidity,
                    liquidity_gross=liquidity,
                    fee_growth_outside_0_x128=0,
                    fee_growth_outside_1_x128=0,
                )
            else:
                tick_data_lower.liquidity_net += liquidity
                tick_data_lower.liquidity_gross += liquidity
            # update upper tick
            tick_data_upper: TickDataUniv3 = ticks_map.get(tick_upper, None)
            if tick_data_upper is None:
                ticks_map[tick_upper] = TickDataUniv3(
                    tick_idx=int(tick_upper),
                    liquidity_net=-liquidity,
                    liquidity_gross=liquidity,
                    fee_growth_outside_0_x128=0,
                    fee_growth_outside_1_x128=0,
                )
            else:
                tick_data_upper.liquidity_net -= liquidity
                tick_data_upper.liquidity_gross += liquidity
        # convert to list
        ticks = list(ticks_map.values())
        return ticks

    def _compute_liquidity_from_liquidity_positions(self, tick: int, data_lps: dict) -> int:
        tick_lower_vec = data_lps["tick_lower"]
        tick_upper_vec = data_lps["tick_upper"]
        lp_amount_vec = data_lps["lp_amount"]
        # assert len(tick_lower_vec) == len(tick_upper_vec) == len(lp_amount_vec)
        liquidity = 0
        for i in range(len(tick_lower_vec)):
            # prepare data
            tick_lower = int(tick_lower_vec[i])
            tick_upper = int(tick_upper_vec[i])
            lp_amount = int(Decimal(lp_amount_vec[i]) * Decimal(self.factor))
            # update liquidity if LP position is in range
            if tick_lower <= tick and tick < tick_upper:
                liquidity += lp_amount
        return liquidity
