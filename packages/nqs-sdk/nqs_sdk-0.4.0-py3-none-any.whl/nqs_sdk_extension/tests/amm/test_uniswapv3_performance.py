import time
import unittest
from typing import Any

import numpy as np
from memory_profiler import memory_usage

from nqs_sdk_extension.protocol import UniswapV3
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.state import StateUniv3
from nqs_sdk_extension.transaction.uniswap import MintTransactionUniv3, SwapTransactionUniv3


class TestProtocolPerformance(unittest.TestCase):
    m = 10_000  # number of swaps
    n = 1_000  # number of mints
    mem_total_limit = 500  # MiB (total memory usage) -> depends on the other tests as well
    mem_delta_limit = 10  # MiB (delta memory usage) -> no idea what is a good value

    def _get_speed_benchmark(self) -> float:
        # benchmark CPU time that should adjust the machine it is running on
        x = 10**18
        start_time = time.time()
        for i in range(1_000):
            x += 1
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time_ms = execution_time * 1000
        print(f"Time to execute 10 additions: {execution_time_ms:.4f} milliseconds")
        return execution_time

    def _prepare_setup(self) -> Any:
        # parameters
        price = 100
        sqrt_price_x96 = 100**0.5 * 2**96
        tick = TickMath.price_to_tick(price, 18, 18)
        # create empty protocol
        state = StateUniv3(
            id=0,
            name="FakePool",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="ETH",
            symbol1="USDC",
            decimals0=18,
            decimals1=18,
            fee_tier=500,
            liquidity=0,
            sqrt_price_x96=sqrt_price_x96,
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=tick,
            ticks=[],  # empty list of ticks
        )
        protocol = UniswapV3(state=state)
        # random seed
        np.random.seed(0)
        # create mints
        lp_prices = price * np.exp(np.random.normal(loc=0.0, scale=0.5, size=(self.n, 2)))
        lp_prices.sort(axis=1)
        liquidities = np.random.exponential(scale=1000 * 10**18, size=self.n)
        mint_transactions = [
            MintTransactionUniv3(
                block_number=0,
                protocol_id="",
                amount=int(liquidities[i]),
                tick_lower=TickMath.price_to_tick(lp_prices[i, 0], 18, 18),
                tick_upper=TickMath.price_to_tick(lp_prices[i, 1], 18, 18),
                sender_wallet=None,
            )
            for i in range(self.n)
        ]
        # create transactions
        amounts = np.random.exponential(scale=1000.0, size=self.m)
        tokens = np.random.choice([0, 1], size=self.m)
        swap_transactions = [
            SwapTransactionUniv3(
                block_number=0,
                protocol_id="",
                amount0_in=int(amounts[i] / price * 10**18) if tokens[i] == 0 else None,
                amount1_in=int(amounts[i] * 10**18) if tokens[i] == 1 else None,
                amount0_out=None,
                amount1_out=None,
                sender_wallet=None,
            )
            for i in range(self.m)
        ]
        return protocol, mint_transactions, swap_transactions

    def test_speed_process_transactions(self) -> None:
        # get benchmark value
        tps_limit = self._get_speed_benchmark()
        # get protocol and transactions
        protocol, mint_transactions, swap_transactions = self._prepare_setup()
        print(f"Starting tick: {protocol.tick}")
        # mints
        start_time = time.time()
        protocol.process_transactions(mint_transactions)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Time to process {self.n:,} mints: {execution_time:.4f} seconds")
        # information about the tick ranges
        print(
            f"Ticks range: min={min(protocol.tickSet)} and max={max(protocol.tickSet)}.",
            f"Number of unique ticks: {len(protocol.tickSet):,}",
        )
        # many swaps
        start_time = time.time()
        # protocol.process_transactions(swap_transactions)
        for swap in swap_transactions:
            protocol.process_single_transaction(swap)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Time to process {self.m:,} swaps: {execution_time:.4f} seconds")
        print(f"Total number of LP ticks crossed: {protocol.n_tick_crossed:,}")
        print(f"Final tick: {protocol.tick}")
        tps_real = execution_time / self.m
        print(f"Time per swap: {tps_real * 1000:.4f} milliseconds")
        self.assertLess(tps_real, tps_limit)

    def test_memory_process_transactions(self) -> None:
        # get protocol and transactions
        protocol, mint_transactions, swap_transactions = self._prepare_setup()
        # many transactions
        protocol.process_transactions(mint_transactions)

        start_mem = memory_usage(max_usage=True)

        # inner function to process transactions
        def process_transactions() -> None:
            for swap in swap_transactions:
                protocol.process_single_transaction(swap)

        mem_usage = memory_usage(proc=process_transactions, max_usage=True, interval=0.01)
        mem_delta = mem_usage - start_mem
        print(f"Memory usage to process {self.m:,} swaps: {mem_usage:.4f} MiB (delta: {mem_delta:.4f} MiB)")
        self.assertLess(start_mem, self.mem_total_limit)
        self.assertLess(mem_delta, self.mem_delta_limit)


if __name__ == "__main__":
    unittest.main()
