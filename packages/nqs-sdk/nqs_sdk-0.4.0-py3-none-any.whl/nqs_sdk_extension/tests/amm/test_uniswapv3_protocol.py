# type: ignore

import copy
import math
import unittest

import pytest
from nqs_pycore import LPTokenUniv3, TokenMetadata, Wallet
from sortedcontainers import SortedDict, SortedSet

from nqs_sdk_extension.protocol import UniswapV3, uniswapv3libs
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath
from nqs_sdk_extension.protocol.amm.uniswapv3.utils import (
    lp_from_amount0_to_liquidity_amount1,
    lp_from_amount1_to_liquidity_amount0,
    lp_from_liquidity_to_amount0_amount1,
)
from nqs_sdk_extension.state import StateUniv3, TickDataUniv3
from nqs_sdk_extension.transaction.uniswap import TransactionHelperUniv3
from nqs_sdk_extension.wallet.utils import AmountNoneError, TickInitializationError, WrongTickRangeError

tran_helper = TransactionHelperUniv3()


class TestSwapStaticMethods(unittest.TestCase):
    def test_zero_for_one(self):
        assert UniswapV3.is_zero_for_one(amount0_in=1.0, amount0_out=None, amount1_in=None, amount1_out=None) is True
        assert UniswapV3.is_zero_for_one(amount0_in=None, amount0_out=None, amount1_in=None, amount1_out=100) is True
        assert UniswapV3.is_zero_for_one(amount0_in=None, amount0_out=None, amount1_in=100, amount1_out=None) is False
        assert UniswapV3.is_zero_for_one(amount0_in=None, amount0_out=100, amount1_in=None, amount1_out=None) is False
        with pytest.raises(AmountNoneError) as excinfo:
            UniswapV3.is_zero_for_one(amount0_in=100, amount0_out=100, amount1_in=None, amount1_out=None)
            assert str(excinfo.value) == "only one amount should be not None for a swap"
        with pytest.raises(AmountNoneError) as excinfo:
            UniswapV3.is_zero_for_one(amount0_in=None, amount0_out=None, amount1_in=None, amount1_out=None)
            assert str(excinfo.value) == "only one amount should be not None for a swap"

    def test_is_exact_input(self):
        assert UniswapV3.is_exact_input(amount0_in=100, amount0_out=None, amount1_in=None, amount1_out=None) is True
        assert UniswapV3.is_exact_input(amount0_in=None, amount0_out=None, amount1_in=100, amount1_out=None) is True
        assert UniswapV3.is_exact_input(amount0_in=None, amount0_out=None, amount1_in=None, amount1_out=100) is False
        assert UniswapV3.is_exact_input(amount0_in=None, amount0_out=100, amount1_in=None, amount1_out=None) is False
        with pytest.raises(AmountNoneError) as excinfo:
            UniswapV3.is_exact_input(amount0_in=100, amount0_out=100, amount1_in=None, amount1_out=None)
            assert str(excinfo.value) == "only one amount should be not None for a swap"
        with pytest.raises(AmountNoneError) as excinfo:
            UniswapV3.is_exact_input(amount0_in=None, amount0_out=None, amount1_in=None, amount1_out=None)
            assert str(excinfo.value) == "only one amount should be not None for a swap"

    def test_constant_product_swap(self):
        assert UniswapV3.constant_product_swap(2.0, 3.0, 0.0) == 0.0
        assert UniswapV3.constant_product_swap(2.0, 3.0, 1.0) == 0.5

    def test_get_virtual_reserves(self):
        assert UniswapV3.get_virtual_reserves(100, 20) == (5, 2_000)
        assert UniswapV3.get_virtual_reserves(100, 200) == (0.5, 20_000)

    def test_get_swap_amount_out(self):
        assert UniswapV3.get_swap_amount_out(False, 2.0, 3.0, 1.0) == 0.5
        assert UniswapV3.get_swap_amount_out(True, 3.0, 2.0, 1.0) == 0.5

    def test_get_post_swap_price(self):
        # initial price is 400, swap one way, then swap back
        assert UniswapV3.get_post_swap_price(False, 5, 2_000, 100) == 441
        amount_out = UniswapV3.get_swap_amount_out(False, 5, 2_000, 100)
        assert UniswapV3.get_post_swap_price(True, 5 - amount_out, 2_100, amount_out) == 400


class TestLiquidityProviderStaticMethods(unittest.TestCase):
    tick_price = TickMath.price_to_tick(4000, 18, 18)
    tick_lower = 82_164
    tick_upper = 83_668
    tick_below = 82_163
    tick_above = 83_669
    sqrt_price = TickMath.tick_to_price(tick_price, 18, 18) ** 0.5
    sqrt_price_lower = TickMath.tick_to_price(tick_lower, 18, 18) ** 0.5
    sqrt_price_upper = TickMath.tick_to_price(tick_upper, 18, 18) ** 0.5
    sqrt_price_below = TickMath.tick_to_price(tick_below, 18, 18) ** 0.5
    sqrt_price_above = TickMath.tick_to_price(tick_above, 18, 18) ** 0.5

    def test_amount0_to_liquidity_amount1(self):
        # price in range
        assert lp_from_amount0_to_liquidity_amount1(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 2.0
        ) == pytest.approx((3_561.138, 8_610.458), 0.001)
        # price below range
        assert lp_from_amount0_to_liquidity_amount1(
            self.sqrt_price_below, self.sqrt_price_lower, self.sqrt_price_upper, 2.0
        ) == pytest.approx((1680.503, 0), 0.001)
        # cannot provide liquidity with token 0 if the range is below the price
        assert lp_from_amount0_to_liquidity_amount1(
            self.sqrt_price_above, self.sqrt_price_lower, self.sqrt_price_upper, 2.0
        ) == (None, None)
        assert lp_from_amount0_to_liquidity_amount1(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 0.0
        ) == (0, 0)

    def test_liquidity_to_amount0_amount1(self):
        # price in range
        assert lp_from_liquidity_to_amount0_amount1(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 3_561.138
        ) == pytest.approx((2.0, 8_610.458), 0.001)
        # price below range
        assert lp_from_liquidity_to_amount0_amount1(
            self.sqrt_price_below, self.sqrt_price_lower, self.sqrt_price_upper, 3_561.138
        ) == pytest.approx((4.238, 0), 0.001)
        # price above range
        assert lp_from_liquidity_to_amount0_amount1(
            self.sqrt_price_above, self.sqrt_price_lower, self.sqrt_price_upper, 3_561.138
        ) == pytest.approx((0, 16_905.080), 0.001)
        assert lp_from_liquidity_to_amount0_amount1(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 0.0
        ) == (0, 0)

    def test_amount1_to_liquidity_amount0(self):
        # price in range
        assert lp_from_amount1_to_liquidity_amount0(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 8_610.458
        ) == pytest.approx((3_561.138, 2.0), 0.001)
        # cannot provide liquidity with token 1 if the range is above the price
        assert lp_from_amount1_to_liquidity_amount0(
            self.sqrt_price_below, self.sqrt_price_lower, self.sqrt_price_upper, 8_610.458
        ) == (None, None)
        # price above range
        assert lp_from_amount1_to_liquidity_amount0(
            self.sqrt_price_above, self.sqrt_price_lower, self.sqrt_price_upper, 8_610.458
        ) == pytest.approx((1_813.835, 0), 0.001)
        assert lp_from_amount1_to_liquidity_amount0(
            self.sqrt_price, self.sqrt_price_lower, self.sqrt_price_upper, 0.0
        ) == (0, 0)

    def test_find_lp_token(self):
        nft0 = LPTokenUniv3(
            pool_name="1",
            token_id="0",
            tick_lower=150,
            tick_upper=200,
            liquidity=200,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        nft1 = LPTokenUniv3(
            pool_name="0",
            token_id="0",
            tick_lower=100,
            tick_upper=200,
            liquidity=100,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        nft2 = LPTokenUniv3(
            pool_name="0",
            token_id="0",
            tick_lower=150,
            tick_upper=200,
            liquidity=200,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        nft3 = LPTokenUniv3(
            pool_name="0",
            token_id="0",
            tick_lower=100,
            tick_upper=250,
            liquidity=300,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        nfts = [nft0, nft1, nft2, nft3]
        holdings = {"ETH": 0, "USDT": 0}
        tokens_metadata = {"ETH": TokenMetadata("Ethereum", "ETH", 0), "USDT": TokenMetadata("us dollar", "USDT", 0)}
        wallet = Wallet(holdings, tokens_metadata, nfts, "agent")
        assert UniswapV3._get_position("0", 150, 200, wallet) == nft2


class TestLiquidityMethods(unittest.TestCase):
    state_empty = StateUniv3(
        id=0,
        name="Uniswap V3",
        block_number=0,
        block_timestamp=0,
        token0="0x0",
        token1="0x1",
        symbol0="ETH",
        symbol1="USDT",
        decimals0=18,
        decimals1=18,
        fee_tier=500,
        liquidity=0,
        sqrt_price_x96=0,
        fee_growth_global_0_x128=0,
        fee_growth_global_1_x128=0,
        tick=250,
        ticks=[],  # empty list of ticks
    )

    def test_net_and_gross_liquidity_after_mints(self):
        protocol = UniswapV3(state=self.state_empty)
        mint_a = tran_helper.create_mint_transaction(amount=2, tick_lower=100, tick_upper=200)
        mint_b = tran_helper.create_mint_transaction(amount=3, tick_lower=200, tick_upper=400)
        mint_c = tran_helper.create_mint_transaction(amount=1, tick_lower=300, tick_upper=500)
        mint_d = tran_helper.create_mint_transaction(amount=1, tick_lower=500, tick_upper=600)
        for mint in [mint_a, mint_b, mint_c, mint_d]:
            protocol._update_from_mint(
                amount=mint.amount,
                amount0=None,
                amount1=None,
                tick_lower=mint.tick_lower,
                tick_upper=mint.tick_upper,
                msg_sender=None,
            )
        ticks = list(protocol.tickSet)
        net_liquidity = [protocol.ticks.get(tick).liquidity_net for tick in ticks]
        gross_liquidity = [protocol.ticks.get(tick).liquidity_gross for tick in ticks]
        assert ticks == [100, 200, 300, 400, 500, 600]
        assert net_liquidity == [2, 1, 1, -3, 0, -1]
        assert gross_liquidity == [2, 5, 1, 3, 2, 1]

    def test_net_and_gross_liquidity_after_burns(self):
        # same mints as above
        protocol = UniswapV3(state=self.state_empty)
        mint_a = tran_helper.create_mint_transaction(amount=2, tick_lower=100, tick_upper=200)
        mint_b = tran_helper.create_mint_transaction(amount=3, tick_lower=200, tick_upper=400)
        mint_c = tran_helper.create_mint_transaction(amount=1, tick_lower=300, tick_upper=500)
        mint_d = tran_helper.create_mint_transaction(amount=1, tick_lower=500, tick_upper=600)
        for mint in [mint_a, mint_b, mint_c, mint_d]:
            protocol._update_from_mint(
                amount=mint.amount,
                amount0=None,
                amount1=None,
                tick_lower=mint.tick_lower,
                tick_upper=mint.tick_upper,
                msg_sender=None,
            )
        # burn all of them
        burn_a = tran_helper.create_burn_transaction(amount=2, tick_lower=100, tick_upper=200)
        burn_b = tran_helper.create_burn_transaction(amount=3, tick_lower=200, tick_upper=400)
        burn_c = tran_helper.create_burn_transaction(amount=1, tick_lower=300, tick_upper=500)
        burn_d = tran_helper.create_burn_transaction(amount=1, tick_lower=500, tick_upper=600)
        for burn in [burn_a, burn_b, burn_c, burn_d]:
            protocol._update_from_burn(
                amount=burn.amount,
                amount0=None,
                amount1=None,
                tick_lower=burn.tick_lower,
                tick_upper=burn.tick_upper,
                msg_sender=None,
            )
        # final ticks state should be empty
        assert SortedSet() == protocol.tickSet
        assert SortedDict() == protocol.ticks


class TestMintBurnMethods(unittest.TestCase):
    decimals0 = 18
    decimals1 = 6
    sqrt_price_x96 = TickMath.get_sqrt_ratio_at_tick(250)
    state_empty = StateUniv3(
        id=0,
        name="Uniswap V3",
        block_number=0,
        block_timestamp=0,
        token0="0x0",
        token1="0x1",
        symbol0="ETH",
        symbol1="USDC",
        decimals0=decimals0,
        decimals1=decimals1,
        fee_tier=500,
        liquidity=0,
        sqrt_price_x96=sqrt_price_x96,
        fee_growth_global_0_x128=0,
        fee_growth_global_1_x128=0,
        tick=250,
        ticks=[],  # empty list of ticks
    )
    liquidity = 100
    amount0, amount1 = lp_from_liquidity_to_amount0_amount1(
        sqrt_price=TickMath.tick_to_price(250, decimals0, decimals1) ** 0.5,
        sqrt_price_lower=TickMath.tick_to_price(100, decimals0, decimals1) ** 0.5,
        sqrt_price_upper=TickMath.tick_to_price(400, decimals0, decimals1) ** 0.5,
        liquidity=liquidity,
    )
    liquidity_int = liquidity * 10 ** (0.5 * (decimals0 + decimals1))
    amount0_int = amount0 * 10**decimals0
    amount1_int = amount1 * 10**decimals1
    rel_error = 10 ** (-0.5 * (decimals0 + decimals1))

    def test_mint_liquidity(self):
        protocol = UniswapV3(state=self.state_empty)
        mint_a = tran_helper.create_mint_transaction(amount=self.liquidity_int, tick_lower=100, tick_upper=400)
        mint_b = tran_helper.create_mint_transaction(amount0=self.amount0_int, tick_lower=100, tick_upper=400)
        mint_c = tran_helper.create_mint_transaction(amount1=self.amount1_int, tick_lower=100, tick_upper=400)
        protocol.process_single_transaction(mint_a)
        assert self.liquidity_int == pytest.approx(protocol.liquidity, rel=self.rel_error)
        protocol.process_single_transaction(mint_b)
        assert 2 * self.liquidity_int == pytest.approx(protocol.liquidity, rel=self.rel_error)
        protocol.process_single_transaction(mint_c)
        assert 3 * self.liquidity_int == pytest.approx(protocol.liquidity, rel=self.rel_error)

    def test_burn_liquidity(self):
        protocol = UniswapV3(state=self.state_empty)
        mint_a = tran_helper.create_mint_transaction(amount=3 * self.liquidity_int, tick_lower=100, tick_upper=400)
        protocol.process_single_transaction(mint_a)
        burn_a = tran_helper.create_burn_transaction(amount=self.liquidity_int, tick_lower=100, tick_upper=400)
        burn_b = tran_helper.create_burn_transaction(amount0=self.amount0_int, tick_lower=100, tick_upper=400)
        burn_c = tran_helper.create_burn_transaction(amount1=self.amount1_int, tick_lower=100, tick_upper=400)
        protocol.process_single_transaction(burn_a)
        assert 2 * self.liquidity_int == pytest.approx(protocol.liquidity, rel=self.rel_error)
        protocol.process_single_transaction(burn_b)
        assert self.liquidity_int == pytest.approx(protocol.liquidity, rel=2 * self.rel_error)  # XXX: not clear why
        protocol.process_single_transaction(burn_c)
        assert protocol.liquidity == pytest.approx(0, abs=1.0)
        with pytest.raises(TickInitializationError) as excinfo:
            protocol.process_single_transaction(burn_c)
        assert str(excinfo.value) == "ticks should be already initialized"

    def test_burn_error(self):
        protocol = UniswapV3(state=self.state_empty)
        mint_a = tran_helper.create_mint_transaction(amount=self.liquidity_int, tick_lower=100, tick_upper=400)
        protocol.process_single_transaction(mint_a)
        burn_a = tran_helper.create_burn_transaction(amount=self.liquidity_int + 11, tick_lower=100, tick_upper=400)
        with pytest.raises(ValueError) as excinfo:
            protocol.process_single_transaction(burn_a)
        print(excinfo.value)
        assert str(excinfo.value) == "cannot burn more liquidity than available - on block : None"

    def test_lp_burn_error(self):
        protocol = UniswapV3(state=self.state_empty)
        lp_token = LPTokenUniv3(
            pool_name=self.state_empty.name,
            token_id=UniswapV3.get_token_id("agent", self.state_empty.name, -100, 100),
            tick_lower=-100,
            tick_upper=100,
            liquidity=200_000,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        wallet = Wallet(
            agent_name="agent",
            holdings={},
            tokens_metadata={},
            erc721_tokens=[lp_token],
        )
        with pytest.raises(Exception) as excinfo:
            protocol._update_position(-100, 100, -300_000, wallet)
            assert str(excinfo.value) == (
                "Failed to execute the burn transaction on token with ID "
                "'agent_Uniswap V3_-100_100' of 'agent'. Trying to remove more "
                "than the total amount of liquidity available."
            )

    def test_custom_token_ids(self):
        protocol = UniswapV3(state=self.state_empty)
        wallet = Wallet(
            holdings={"ETH": 1_000, "USDC": 1_000},
            tokens_metadata={"ETH": TokenMetadata("Ethereum", "ETH", 0), "USDC": TokenMetadata("us dollar", "USDT", 0)},
            agent_name="agent",
            erc721_tokens=[],
        )
        mint_a = tran_helper.create_mint_transaction(amount=100, tick_lower=100, tick_upper=400, sender_wallet=wallet)
        mint_b = tran_helper.create_mint_transaction(
            amount=100, tick_lower=100, tick_upper=400, sender_wallet=wallet, token_id="a"
        )
        mint_b2 = tran_helper.create_mint_transaction(
            amount=100, tick_lower=100, tick_upper=400, sender_wallet=wallet, token_id="a"
        )
        mint_c = tran_helper.create_mint_transaction(
            amount0=1, tick_lower=200, tick_upper=400, sender_wallet=wallet, token_id="a"
        )
        burn_a = tran_helper.create_burn_transaction(
            amount=100, tick_lower=100, tick_upper=400, sender_wallet=wallet, token_id="a"
        )
        burn_b = tran_helper.create_burn_transaction(
            amount=100, tick_lower=200, tick_upper=400, sender_wallet=wallet, token_id="a"
        )
        protocol.process_single_transaction(mint_a)
        protocol.process_single_transaction(mint_b)
        lp_token = wallet.get_erc721_token("a")  # TODO investigate the cast
        assert lp_token.liquidity == 100
        protocol.process_single_transaction(mint_b2)
        lp_token = wallet.get_erc721_token("a")
        assert lp_token.liquidity == 100 * 2
        with pytest.raises(WrongTickRangeError) as excinfo:
            protocol.process_single_transaction(mint_c)
        assert str(excinfo.value) == (
            "Attempting to modify the existing position a on a wrong tick range. NFT tick range: 100, 400, "
            "requested tick range: 200, 400."
        )

        protocol.process_single_transaction(burn_a)
        lp_token = wallet.get_erc721_token("a")
        assert lp_token.liquidity == 100
        with pytest.raises(WrongTickRangeError) as excinfo:
            protocol.process_single_transaction(burn_b)
        assert str(excinfo.value) == (
            "Attempting to modify the existing position a on a wrong tick range. NFT tick range: 100, 400, "
            "requested tick range: 200, 400."
        )


class TestFeeMethods(unittest.TestCase):
    def test_fee_collected_from_outside_from_above_and_from_below(self):
        """
        Stylized example with tree ticks: t1, t2, t3
        We monitor the fee variables at tick t2
        """
        # ticks
        t2 = TickDataUniv3(
            liquidity_gross=0,  # not relevant here
            liquidity_net=0,  # not relevant here
            fee_growth_outside_0_x128=0,
            fee_growth_outside_1_x128=0,
            tick_idx=200,
        )
        # this is not a realistic pool state as it has only one tick
        state = StateUniv3(
            id=0,
            name="Uniswap V3",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="ETH",
            symbol1="USDT",
            decimals0=18,
            decimals1=18,
            fee_tier=500,
            liquidity=0,  # not relevant here
            sqrt_price_x96=0,  # not relevant here
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=100,
            ticks=[t2],
        )
        protocol = UniswapV3(state=state)
        # t1 -> t2 collected fee 10Y
        protocol.fee_growth_global_1_x128 += 10
        assert protocol._get_fee_growth_below(200, True) == 0
        assert protocol._get_fee_growth_above(200, True) == 0
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 0
        # t2 tick cross
        protocol.tick_cross(200, protocol.fee_growth_global_0_x128, protocol.fee_growth_global_1_x128)
        protocol.tick = 200
        assert protocol.ticks.get(200).fee_growth_outside_0_x128 == 0
        assert protocol.ticks.get(200).fee_growth_outside_1_x128 == 10
        assert protocol._get_fee_growth_below(200, True) == 0
        assert protocol._get_fee_growth_above(200, True) == 0
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 0
        # t2 -> t3 collected fee 15Y
        protocol.fee_growth_global_1_x128 += 15
        assert protocol._get_fee_growth_below(200, True) == 0
        assert protocol._get_fee_growth_above(200, True) == 0
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 15
        # t2 <- t3 collected fee 4X
        protocol.fee_growth_global_0_x128 += 4
        assert protocol._get_fee_growth_below(200, True) == 0
        assert protocol._get_fee_growth_above(200, True) == 4
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 15
        # t2 tick cross
        protocol.tick_cross(200, protocol.fee_growth_global_0_x128, protocol.fee_growth_global_1_x128)
        protocol.tick = 100
        assert protocol.ticks.get(200).fee_growth_outside_0_x128 == 4
        assert protocol.ticks.get(200).fee_growth_outside_1_x128 == 15
        assert protocol._get_fee_growth_below(200, True) == 0
        assert protocol._get_fee_growth_above(200, True) == 4
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 15
        # t1 <- t2 collected fee 3X
        protocol.fee_growth_global_0_x128 += 3
        assert protocol._get_fee_growth_below(200, True) == 3
        assert protocol._get_fee_growth_above(200, True) == 4
        assert protocol._get_fee_growth_below(200, False) == 10
        assert protocol._get_fee_growth_above(200, False) == 15

    def test_fee_collected_inside(self):
        # ticks
        t1 = TickDataUniv3(
            liquidity_gross=0,  # not relevant here
            liquidity_net=0,  # not relevant here
            fee_growth_outside_0_x128=1,
            fee_growth_outside_1_x128=4,
            tick_idx=100,
        )
        t2 = TickDataUniv3(
            liquidity_gross=0,  # not relevant here
            liquidity_net=0,  # not relevant here
            fee_growth_outside_0_x128=4,
            fee_growth_outside_1_x128=15,
            tick_idx=200,
        )
        # this is not a realistic pool state as it has only one tick
        state = StateUniv3(
            id=0,
            name="Uniswap V3",
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="ETH",
            symbol1="USDT",
            decimals0=18,
            decimals1=18,
            fee_tier=500,
            liquidity=0,  # not relevant here
            sqrt_price_x96=0,  # not relevant here
            fee_growth_global_0_x128=7,
            fee_growth_global_1_x128=25,
            tick=150,
            ticks=[t1, t2],
        )
        protocol = UniswapV3(state=state)
        assert protocol._get_fee_growth_inside(100, 200, True) == 2
        assert protocol._get_fee_growth_inside(100, 200, False) == 6


class TestTokenIDMethods(unittest.TestCase):
    def test_get_token_id(self):
        assert UniswapV3.get_token_id("agent0", "pool0", -123, 456) == "agent0_pool0_-123_456"
        with self.assertRaises(AssertionError):
            UniswapV3.get_token_id("agent0", "pool0", -123, -456)


class TestCollectFeeMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.pool_name = "pool0"
        self.state_empty = StateUniv3(
            id=0,
            name=self.pool_name,
            block_number=0,
            block_timestamp=0,
            token0="0x0",
            token1="0x1",
            symbol0="ETH",
            symbol1="USDT",
            decimals0=0,
            decimals1=0,
            fee_tier=10_000,  # 1% fees
            liquidity=0,
            sqrt_price_x96=uniswapv3libs.TickMath.get_sqrt_ratio_at_tick(0),
            fee_growth_global_0_x128=0,
            fee_growth_global_1_x128=0,
            tick=0,
            ticks=[],  # empty list of ticks
        )
        self.mint1 = tran_helper.create_mint_transaction(amount=100_000, tick_lower=-100, tick_upper=100)
        self.mint2 = tran_helper.create_mint_transaction(amount=100_000, tick_lower=-100, tick_upper=100)
        self.holdings = {"ETH": 0, "USDT": 0}
        self.tokens_metadata = {
            "ETH": TokenMetadata("Ethereum", "ETH", 0),
            "USDT": TokenMetadata("us dollar", "USDT", 0),
        }
        # LP position
        agent_name = "agent0"
        token_id = token_id = UniswapV3.get_token_id(agent_name, self.pool_name, -100, 100)
        self.lp_token1 = LPTokenUniv3(
            pool_name=self.pool_name,
            token_id=token_id,
            tick_lower=-100,
            tick_upper=100,
            liquidity=100_000,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        self.wallet1 = Wallet(
            agent_name=agent_name,
            holdings=self.holdings,
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[self.lp_token1],
        )
        # LP collect transaction
        self.collect1 = tran_helper.create_collect_transaction(
            tick_lower=-100, tick_upper=100, sender_wallet=self.wallet1
        )

    def test_collect_fee_one_lp_token0_in(self):
        # trader
        swap1 = tran_helper.create_swap_transaction(amount0_in=100)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([self.mint1, swap1, self.collect1])
        collected_fee_eth = self.wallet1.get_balance_of("ETH")
        collected_fee_usdt = self.wallet1.get_balance_of("USDT")
        assert collected_fee_eth == 1
        assert collected_fee_usdt == 0

    def test_collect_fee_one_lp_token1_in(self):
        # trader
        swap2 = tran_helper.create_swap_transaction(amount1_in=100)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([self.mint1, swap2, self.collect1])
        collected_fee_eth = self.wallet1.get_balance_of("ETH")
        collected_fee_usdt = self.wallet1.get_balance_of("USDT")
        assert collected_fee_eth == 0
        assert collected_fee_usdt == 1

    def test_collect_fee_one_lp_token0_out(self):
        # trader
        wallet2 = Wallet(
            holdings={"ETH": 1_000, "USDT": 1_000},
            tokens_metadata=self.tokens_metadata,
            agent_name="agent",
            erc721_tokens=[],
        )
        swap3 = tran_helper.create_swap_transaction(amount0_out=100, sender_wallet=wallet2)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([self.mint1, swap3, self.collect1])
        # Get fee amounts
        fee_usdt = math.ceil(0.01 * (1_000 - wallet2.get_balance_of("USDT")))
        assert self.wallet1.get_balance_of("ETH") == 0
        assert self.wallet1.get_balance_of("USDT") == fee_usdt

    def test_collect_fee_one_lp_token1_out(self):
        # trader
        wallet2 = Wallet(
            holdings={"ETH": 1_000, "USDT": 1_000},
            tokens_metadata=self.tokens_metadata,
            agent_name="agent",
            erc721_tokens=[],
        )
        swap4 = tran_helper.create_swap_transaction(amount1_out=100, sender_wallet=wallet2)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([self.mint1, swap4, self.collect1])
        # Get fee amounts
        fee_eth = math.ceil(0.01 * (1_000 - wallet2.get_balance_of("ETH")))
        assert self.wallet1.get_balance_of("ETH") == fee_eth
        assert self.wallet1.get_balance_of("USDT") == 0

    def test_collect_fee_two_lp_token0_in(self):
        # Update liquidity of lp token 1
        self.lp_token1.liquidity = 800_000
        self.wallet1.replace_erc721_token(self.lp_token1)
        # LP positions with same ticks
        agent_name = "agent1"
        token_id = UniswapV3.get_token_id(agent_name, self.pool_name, -100, 100)
        lp_token2 = LPTokenUniv3(
            pool_name=self.pool_name,
            token_id=token_id,
            tick_lower=-100,
            tick_upper=100,
            liquidity=200_000,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        wallet2 = Wallet(
            agent_name=agent_name,
            holdings=self.holdings,
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[lp_token2],
        )
        # LP collect transactions
        collect2 = tran_helper.create_collect_transaction(tick_lower=-100, tick_upper=100, sender_wallet=wallet2)
        # trader
        swap1 = tran_helper.create_swap_transaction(amount0_in=1_000)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.liquidity = 1_000_000  # hack
        protocol.process_transactions([self.mint1, swap1, self.collect1, collect2])
        # Check fees
        collected_fee_eth1 = self.wallet1.get_balance_of("ETH")
        collected_fee_usdt1 = self.wallet1.get_balance_of("USDT")
        collected_fee_eth2 = wallet2.get_balance_of("ETH")
        collected_fee_usdt2 = wallet2.get_balance_of("USDT")
        assert collected_fee_eth1 + collected_fee_eth2 == 10
        assert collected_fee_usdt1 + collected_fee_usdt2 == 0
        assert collected_fee_eth1 == 8
        assert collected_fee_usdt1 == 0
        assert collected_fee_eth2 == 2
        assert collected_fee_usdt2 == 0

    def test_collect_fee_two_lp_token1_in(self):
        # Update liquidity of lp token 1
        self.lp_token1.liquidity = 800_000
        self.wallet1.replace_erc721_token(self.lp_token1)
        # LP positions with same ticks
        agent_name = "agent1"
        token_id = UniswapV3.get_token_id(agent_name, self.pool_name, -100, 100)
        lp_token2 = LPTokenUniv3(
            pool_name=self.pool_name,
            token_id=token_id,
            tick_lower=-100,
            tick_upper=100,
            liquidity=200_000,
            fee_growth_inside_0_last_x128=0,
            fee_growth_inside_1_last_x128=0,
            tokens_owed_0=0,
            tokens_owed_1=0,
        )
        wallet2 = Wallet(
            agent_name=agent_name,
            holdings=self.holdings,
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[lp_token2],
        )
        # LP collect transactions
        collect2 = tran_helper.create_collect_transaction(tick_lower=-100, tick_upper=100, sender_wallet=wallet2)
        # trader
        swap2 = tran_helper.create_swap_transaction(amount1_in=1_000)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.liquidity = 1_000_000  # hack
        protocol.process_transactions([self.mint1, swap2, self.collect1, collect2])
        # Check fees
        collected_fee_eth1 = self.wallet1.get_balance_of("ETH")
        collected_fee_usdt1 = self.wallet1.get_balance_of("USDT")
        collected_fee_eth2 = wallet2.get_balance_of("ETH")
        collected_fee_usdt2 = wallet2.get_balance_of("USDT")
        # XXX rounding down the integer, not clear why (very small decimal difference as 1 = 10**-decimal)
        precision = 1
        assert abs(collected_fee_eth1 - 0) <= precision
        assert abs(collected_fee_usdt1 - 8) <= precision
        assert abs(collected_fee_eth2 - 0) <= precision
        assert abs(collected_fee_usdt2 - 2) <= precision

    # Test that the tokens owed are computed and updated properly, before and after the fee collection LP position
    def test_collect_fee_tokens_owed(self):
        # LP burn transaction
        burn1 = tran_helper.create_burn_transaction(
            amount=100_000, tick_lower=-100, tick_upper=100, sender_wallet=self.wallet1
        )
        # trader
        swap1 = tran_helper.create_swap_transaction(amount0_in=100)
        # Run transactions
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_single_transaction(self.mint1)
        lp_token1 = self.wallet1.get_erc721_tokens()[0]
        # Fee owed before the transaction
        assert (lp_token1.tokens_owed_0, lp_token1.tokens_owed_1) == (0, 0)
        assert protocol.get_total_tokens_owed(lp_token1) == (0, 0)
        # Fee owed after the transaction
        protocol.process_single_transaction(swap1)
        lp_token1 = self.wallet1.get_erc721_tokens()[0]
        assert (lp_token1.tokens_owed_0, lp_token1.tokens_owed_1) == (0, 0)
        assert protocol.get_total_tokens_owed(lp_token1) == (1, 0)
        # Fee owed after the LP position is burned
        protocol.process_single_transaction(burn1)
        lp_token1 = self.wallet1.get_erc721_tokens()[0]
        assert (lp_token1.tokens_owed_0, lp_token1.tokens_owed_1) == (0, 0)
        assert protocol.get_total_tokens_owed(lp_token1) == (0, 0)
        # Fee owed after the fee collection
        protocol.process_single_transaction(self.collect1)
        lp_token1 = self.wallet1.get_erc721_tokens()[0]
        assert (lp_token1.tokens_owed_0, lp_token1.tokens_owed_1) == (0, 0)
        assert protocol.get_total_tokens_owed(lp_token1) == (0, 0)


class TestSwapMethods(unittest.TestCase):
    """
    Test swaps methods on approximated values computed by hand.
    TODO: The test precisions should be double checked and improved.
    """

    tick_init = uniswapv3libs.TickMath.price_to_tick(3800, 18, 18)
    state_empty = StateUniv3(
        id=0,
        name="pool0",
        block_number=0,
        block_timestamp=0,
        token0="0x0",
        token1="0x1",
        symbol0="ETH",
        symbol1="USDC",
        decimals0=18,
        decimals1=18,  # for the example only
        fee_tier=3000,
        liquidity=0,
        sqrt_price_x96=3800**0.5 * 2**96,
        fee_growth_global_0_x128=0,
        fee_growth_global_1_x128=0,
        tick=tick_init,
        ticks=[],  # empty list of ticks
    )
    tokens_metadata = {
        "ETH": TokenMetadata("ethereum", "ETH", 18),
        "USDC": TokenMetadata("us dollar", "USDC", 18),
    }  # XXX
    # LP A mints 3 ETH between t1=3600.005212 and t3=3999.742678
    wallet_a = Wallet(
        holdings={"ETH": 3.5, "USDC": 100_000}, tokens_metadata=tokens_metadata, agent_name="Agent_A", erc721_tokens=[]
    )
    mint_a = tran_helper.create_mint_transaction(
        amount0=3 * 10**18, tick_lower=81_891, tick_upper=82_944, sender_wallet=wallet_a
    )
    LA = 7312.6996  # 3 / (1/(3800)**0.5 - 1/(1.0001**82_944)**0.5)
    # mint_a = tran_helper.create_mint_transaction(
    #    amount=int(7_312.6996 * 10**18), tick_lower=81_891, tick_upper=82_944, sender_wallet=wallet_a)
    # LP B mints 10 ETH between t2=3899.823492 and t4=4099.761469
    wallet_b = Wallet(
        holdings={"ETH": 10, "USDC": 5_000}, tokens_metadata=tokens_metadata, agent_name="Agent_B", erc721_tokens=[]
    )
    mint_b = tran_helper.create_mint_transaction(
        amount0=10 * 10**18, tick_lower=82_691, tick_upper=83_191, sender_wallet=wallet_b
    )
    LB = 25_294.2124  # 10 / (1/(1.0001**82_691)**0.5 - 1/(1.0001**83_191)**0.5)
    # Trade 1 swaps USDC for 1 ETH
    wallet1 = Wallet(
        holdings={"ETH": 0, "USDC": 4_000}, tokens_metadata=tokens_metadata, agent_name="Agent_1", erc721_tokens=[]
    )
    trade1 = tran_helper.create_swap_transaction(amount0_out=1 * 10**18, sender_wallet=wallet1)
    amount1_in = 3_843.83684
    price1 = 3_864.8853
    # Trade 2 swaps 5_000 USDC for ETH
    wallet2 = Wallet(
        holdings={"ETH": 0, "USDC": 5_000}, tokens_metadata=tokens_metadata, agent_name="Agent_2", erc721_tokens=[]
    )
    trade2 = tran_helper.create_swap_transaction(amount1_in=5_000 * 10**18, sender_wallet=wallet2)
    amount0_out = 1.2795
    price2 = 3_911.0729
    # Fee collection
    fee_a = 19.68
    fee_b = 6.85

    def test_swap_same_tick_interval(self):
        mint_a = copy.deepcopy(self.mint_a)
        mint_b = copy.deepcopy(self.mint_b)
        trade1 = copy.deepcopy(self.trade1)
        protocol = UniswapV3(state=self.state_empty)
        assert protocol.liquidity * 10**-18 == 0
        protocol.process_single_transaction(mint_a)
        assert abs(mint_a.sender_wallet.get_erc721_tokens()[0].liquidity * 10**-18 - self.LA) <= 0.01
        protocol.process_single_transaction(mint_b)
        print(mint_b.sender_wallet.get_erc721_tokens()[0].liquidity * 10**-18)
        assert abs(mint_b.sender_wallet.get_erc721_tokens()[0].liquidity * 10**-18 - self.LB) <= 0.01
        assert abs(protocol.liquidity * 10**-18 - self.LA) <= 0.01
        protocol.process_single_transaction(trade1)
        assert abs(4_000 - trade1.sender_wallet.holdings["USDC"] * 10**-18 - self.amount1_in) <= 0.25
        assert abs(TickMath.tick_to_price(protocol.tick, 18, 18) - self.price1) <= 0.40

    def test_swap_multi_tick_intervals(self):
        mint_a = copy.deepcopy(self.mint_a)
        mint_b = copy.deepcopy(self.mint_b)
        trade1 = copy.deepcopy(self.trade1)
        trade2 = copy.deepcopy(self.trade2)
        # same as above
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([mint_a, mint_b, trade1])
        # cross tick t2
        protocol.process_single_transaction(trade2)
        assert abs(trade2.sender_wallet.holdings["ETH"] * 10**-18 - self.amount0_out) <= 0.01
        assert abs(TickMath.tick_to_price(protocol.tick, 18, 18) - self.price2) <= 0.35

    def test_swap_multi_tick_intervals_fees_collected(self):
        mint_a = copy.deepcopy(self.mint_a)
        mint_b = copy.deepcopy(self.mint_b)
        trade1 = copy.deepcopy(self.trade1)
        trade2 = copy.deepcopy(self.trade2)
        collect_a = tran_helper.create_collect_transaction(
            tick_lower=81_891, tick_upper=82_944, sender_wallet=mint_a.sender_wallet
        )
        collect_b = tran_helper.create_collect_transaction(
            tick_lower=82_691, tick_upper=83_191, sender_wallet=mint_b.sender_wallet
        )
        # same as above
        protocol = UniswapV3(state=self.state_empty)
        protocol.process_transactions([mint_a, mint_b, trade1, trade2])
        # LP A and B collect fees
        usdc_a = collect_a.sender_wallet.get_balance_of("USDC")
        usdc_b = collect_b.sender_wallet.get_balance_of("USDC")
        protocol.process_transactions([collect_a, collect_b])
        fee_a = collect_a.sender_wallet.get_balance_of("USDC") - usdc_a
        fee_b = collect_b.sender_wallet.get_balance_of("USDC") - usdc_b
        assert abs(fee_a * 10**-18 - self.fee_a) <= 0.02
        assert abs(fee_b * 10**-18 - self.fee_b) <= 0.02


if __name__ == "__main__":
    # unittest.main()
    # Run only one test
    # suite = unittest.TestSuite()
    # suite.addTest(TestCollectFeeMethods("test_collect_fee_one_lp_token1_in"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
    unittest.main()
