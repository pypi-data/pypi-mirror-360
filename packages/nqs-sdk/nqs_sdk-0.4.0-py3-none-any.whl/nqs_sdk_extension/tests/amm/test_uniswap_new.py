import copy
import unittest

from nqs_pycore import TokenMetadata, Wallet

from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk_extension.state.uniswap import StateUniv3
from nqs_sdk_extension.transaction.uniswap import TransactionHelperUniv3


class TestUniswapNew(unittest.TestCase):
    def test_uniswap_new(self) -> None:
        uniswap_state = StateUniv3(
            id=0,
            name="UniswapV3",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="USDC",
            symbol1="ETH",
            decimals0=6,
            decimals1=18,
            fee_tier=500,
            liquidity=0,
            sqrt_price_x96=TickMath.price_to_sqrt_price_x96(TickMath.tick_to_price(1, 6, 18), 6, 18),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=0,
            ticks=[],
        )

        wallet = Wallet(
            holdings={"USDC": 1_000_000, "ETH": 1_000_000},
            tokens_metadata={
                "USDC": TokenMetadata(name="0x", symbol="USDC", decimals=6),
                "ETH": TokenMetadata(name="0x", symbol="ETH", decimals=18),
            },
            erc721_tokens=[],
            agent_name="test_agent",
        )

        usdc = wallet.get_balance_of("USDC")
        eth = wallet.get_balance_of("ETH")
        self.assertEqual(usdc, 1000000000000)
        self.assertEqual(eth, 1000000000000000000000000)

        uniswap_pool = UniswapV3(uniswap_state)

        mint = TransactionHelperUniv3.create_mint_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=wallet,
            tick_lower=-887272,
            tick_upper=887272,
            amount=10_000,
        )

        uniswap_pool.process_single_transaction(mint)

        swap = TransactionHelperUniv3.create_swap_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=wallet,
            amount0_in=1_000,
        )

        uniswap_pool.process_single_transaction(swap)

        burn = TransactionHelperUniv3.create_burn_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=wallet,
            amount=10_000,
            tick_lower=-887272,
            tick_upper=887272,
        )

        uniswap_pool.process_single_transaction(burn)

        collect = TransactionHelperUniv3.create_collect_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=wallet,
            tick_lower=-887272,
            tick_upper=887272,
        )

        uniswap_pool.process_single_transaction(collect)

        usdc = wallet.get_balance_of("USDC")
        eth = wallet.get_balance_of("ETH")
        self.assertEqual(usdc, 1000000000000)
        self.assertEqual(eth, 1000000000000000000000000)

    def test_uniswap_edited_attributes(self) -> None:
        uniswap_state = StateUniv3(
            id=0,
            name="UniswapV3",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="USDC",
            symbol1="ETH",
            decimals0=6,
            decimals1=18,
            fee_tier=500,
            liquidity=0,
            sqrt_price_x96=TickMath.price_to_sqrt_price_x96(TickMath.tick_to_price(1, 6, 18), 6, 18),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=0,
            ticks=[],
        )

        uniswap_pool = UniswapV3(uniswap_state)

        mint = TransactionHelperUniv3.create_mint_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            tick_lower=-887272,
            tick_upper=887272,
            amount=100,
        )

        mint_2 = TransactionHelperUniv3.create_mint_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=None,
            tick_lower=-100,
            tick_upper=100,
            amount=1000,
        )

        uniswap_pool.process_single_transaction(mint)
        uniswap_pool.process_single_transaction(mint_2)

        ticks_after_mint = copy.deepcopy(uniswap_pool.ticks)

        # This swap is too big and should revert
        swap = TransactionHelperUniv3.create_swap_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=None,
            amount0_in=1000000000000000000000000,
        )

        uniswap_pool.process_single_transaction(swap)

        ticks_after_swap = copy.deepcopy(uniswap_pool.ticks)
        # The ticks should not change
        self.assertEqual(ticks_after_mint, ticks_after_swap)

        # This swap should be successful but will change the tick from outside the -100, 100 interval
        swap_2 = TransactionHelperUniv3.create_swap_transaction(
            block_number=0,
            protocol_id="UniswapV3",
            sender_wallet=None,
            amount1_in=100000,
        )

        uniswap_pool.process_single_transaction(swap_2)

        ticks_after_swap_2 = copy.deepcopy(uniswap_pool.ticks)
        # The ticks should change
        self.assertNotEqual(ticks_after_mint, ticks_after_swap_2)


if __name__ == "__main__":
    unittest.main()
