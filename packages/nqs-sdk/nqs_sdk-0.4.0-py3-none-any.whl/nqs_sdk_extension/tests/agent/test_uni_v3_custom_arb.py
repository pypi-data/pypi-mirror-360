import unittest

import numpy as np

from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk_extension.state.uniswap import StateUniv3, TickDataUniv3
from nqs_sdk_extension.transaction.uniswap import MintTransactionUniv3, SwapTransactionUniv3


class TestUniswapV3Arbitrageur(unittest.TestCase):
    def test_one_arbitrage(self) -> None:
        liquidity = int((10_000_000 / np.sqrt(2000)) * (10**18))

        tick0 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=-887272,
        )

        tick1 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=-1 * liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=887272,
        )

        pool_state = StateUniv3(
            id=0,
            name="Uni test",
            block_number=0,
            block_timestamp=0,
            symbol0="ETH",
            symbol1="USDC",
            token0="0xETH",
            token1="0xUSDC",
            decimals0=18,
            decimals1=18,
            fee_tier=int(0.0005 * 1e6),
            liquidity=liquidity,
            sqrt_price_x96=int(np.sqrt(2000) * (2**96)),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=TickMath.price_to_tick(2000, 18, 18),
            ticks=[tick0, tick1],
        )

        uni_pool = UniswapV3(pool_state)

        uni_observer = UniswapV3Observer(uni_pool)

        initial_dex_spot = uni_pool.get_spot()
        market_spot = initial_dex_spot + 100
        uni_observer.arbitrage_prices = (initial_dex_spot, market_spot)

        amount_0, amount_1 = uni_observer._get_arbitrage_value()

        swap = SwapTransactionUniv3(
            amount0_in=amount_0,
            amount1_in=amount_1,
            block_number=2,
            sender_wallet=None,
            protocol_id="0",
        )

        uni_pool.process_single_transaction(swap)

        arbitraged_spot = uni_pool.get_spot()
        self.assertNotEqual(initial_dex_spot, arbitraged_spot, "Initial spot should be different from arbitraged spot")
        self.assertGreaterEqual(
            abs(initial_dex_spot / market_spot - 1),
            uni_pool.fee_tier * 1e-6,
            "Initial spot should be different from market spot",
        )
        self.assertLess(
            abs(arbitraged_spot / market_spot - 1),
            uni_pool.fee_tier * 1e-6,
            "Arbitrged spot should be closer to market spot",
        )

    def test_two_sides_arbitrage(self) -> None:
        liquidity = int((10_000_000 / np.sqrt(2000)) * (10**18))

        tick0 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=-887272,
        )
        tick1 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=-1 * liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=887272,
        )

        pool_state = StateUniv3(
            id=0,
            name="Uni test",
            block_number=0,
            block_timestamp=0,
            symbol0="ETH",
            symbol1="USDC",
            token0="0xETH",
            token1="0xUSDC",
            decimals0=18,
            decimals1=18,
            fee_tier=int(0.0005 * 1e6),
            liquidity=liquidity,
            sqrt_price_x96=int(np.sqrt(2000) * (2**96)),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=TickMath.price_to_tick(2000, 18, 18),
            ticks=[tick0, tick1],
        )

        uni_pool = UniswapV3(pool_state)

        uni_observer = UniswapV3Observer(uni_pool)

        initial_dex_spot = uni_pool.get_spot()
        market_spot_1 = initial_dex_spot + 10

        uni_observer.arbitrage_prices = (initial_dex_spot, market_spot_1)

        amount_1_0, amount_1_1 = uni_observer._get_arbitrage_value()

        market_spot_2 = initial_dex_spot - 10

        uni_observer.arbitrage_prices = (initial_dex_spot, market_spot_2)

        amount_2_0, amount_2_1 = uni_observer._get_arbitrage_value()

        self.assertIsNone(amount_1_0, "Amount should be None")
        self.assertIsNone(amount_2_1, "Amount should be None")
        self.assertIsNotNone(amount_1_1, "Amount should not be None")
        self.assertIsNotNone(amount_2_0, "Amount should not be None")
        self.assertLessEqual(abs(amount_1_1 / initial_dex_spot / amount_2_0 - 1), 1e-2, "Amount should be the same")  # type: ignore

    def test_empty_pool_arbitrage(self) -> None:
        spot = 0.9995
        liquidity = int((10_000_000 / np.sqrt(spot)) * (10**6))
        tick0 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=-10,
        )
        tick1 = TickDataUniv3(
            liquidity_gross=liquidity,
            liquidity_net=-1 * liquidity,
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=10,
        )

        pool_state = StateUniv3(
            id=0,
            name="Uni test",
            block_number=0,
            block_timestamp=0,
            symbol0="USDC",
            symbol1="USDT",
            token0="0xUSDC",
            token1="0xUSDT",
            decimals0=6,
            decimals1=6,
            fee_tier=int(0.0001 * 1_000_000),
            liquidity=liquidity,
            sqrt_price_x96=TickMath.price_to_sqrt_price_x96(spot, 6, 6),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=TickMath.price_to_tick(spot, 6, 6),
            ticks=[tick0, tick1],
        )

        uni_pool = UniswapV3(pool_state)
        uni_observer = UniswapV3Observer(uni_pool)

        mint_txn_1 = MintTransactionUniv3(
            tick_lower=20,
            tick_upper=30,
            amount=int(0.02 * uni_pool.liquidity),
            block_number=1,
            sender_wallet=None,
            protocol_id="0",
        )

        uni_pool.process_single_transaction(mint_txn_1)
        market_spot = 10
        uni_observer.arbitrage_prices = (uni_pool.get_spot(), market_spot)

        amount0, amount1 = uni_observer._get_arbitrage_value()

        arb_txn = SwapTransactionUniv3(
            amount0_in=amount0,
            amount1_in=amount1,
            block_number=1,
            sender_wallet=None,
            protocol_id="0",
        )

        uni_pool.process_single_transaction(arb_txn)

        self.assertLessEqual(uni_pool.get_spot(), market_spot, "Arbitrageur should not be able to close the gap")


if __name__ == "__main__":
    unittest.main()
