# type: ignore

import unittest

import pytest

from nqs_sdk_extension.protocol.amm.uniswapv3.full_math import FullMath
from nqs_sdk_extension.protocol.amm.uniswapv3.sqrt_price_math import SqrtPriceMath
from nqs_sdk_extension.protocol.amm.uniswapv3.swap_math import SwapMath
from nqs_sdk_extension.protocol.amm.uniswapv3.tick_math import TickMath

# TODO: add more tests with specific values when the TickMath is validated


class TestFullMath(unittest.TestCase):
    def test_mul_div(self):
        a = 10
        b = 20
        denominator = 5

        # Test with valid inputs
        result = FullMath.mul_div(a, b, denominator)
        self.assertEqual(result, 40)

        # Test with denominator = 0, should raise an AssertionError
        with self.assertRaises(AssertionError):
            FullMath.mul_div(a, b, 0)

    def test_mul_div_rounding_up(self):
        a = 10
        b = 20
        denominator = 3

        # Test with valid inputs
        result = FullMath.mul_div_rounding_up(a, b, denominator)
        self.assertEqual(result, 67)

        # Test with (a * b) % denominator = 0, result should not increment
        result = FullMath.mul_div_rounding_up(a, b, 5)
        self.assertEqual(result, 40)

        # Test with result = (1 << 256) - 1 (not rounding up the max of uint256), should raise an AssertionError
        # with self.assertRaises(AssertionError):
        #    FullMath.mul_div_rounding_up((1 << 256) - 1, 1, 1)


class TestSqrtPriceMath(unittest.TestCase):
    def test_get_next_sqrt_price_from_amount0_rounding_up(self):
        sqrt_p_x96 = 10
        liquidity = 20
        amount = 5
        add = True

        # Test with valid inputs
        result = SqrtPriceMath.get_next_sqrt_price_from_amount0_rounding_up(sqrt_p_x96, liquidity, amount, add)
        self.assertIsNotNone(result)

        # Test with amount = 0, should return sqrt_p_x96
        result = SqrtPriceMath.get_next_sqrt_price_from_amount0_rounding_up(sqrt_p_x96, liquidity, 0, add)
        self.assertEqual(result, sqrt_p_x96)

    def test_get_next_sqrt_price_from_amount1_rounding_down(self):
        sqrt_p_x96 = 10
        liquidity = 20
        amount = 5
        add = True

        # Test with valid inputs
        result = SqrtPriceMath.get_next_sqrt_price_from_amount1_rounding_down(sqrt_p_x96, liquidity, amount, add)
        self.assertIsNotNone(result)

        # Test with sqrt_p_x96 <= quotient, should raise an AssertionError
        with self.assertRaises(AssertionError):
            SqrtPriceMath.get_next_sqrt_price_from_amount1_rounding_down(1, liquidity, amount, False)

    def test_get_next_sqrt_price_from_input(self):
        sqrt_p_x96 = 10
        liquidity = 20
        amount_in = 5
        zero_for_one = True

        # Test with valid inputs
        result = SqrtPriceMath.get_next_sqrt_price_from_input(sqrt_p_x96, liquidity, amount_in, zero_for_one)
        self.assertIsNotNone(result)

        # Test with zero_for_one = False
        result = SqrtPriceMath.get_next_sqrt_price_from_input(sqrt_p_x96, liquidity, amount_in, False)
        self.assertIsNotNone(result)

    def test_get_next_sqrt_price_from_output(self):
        sqrt_p_x96 = TickMath.get_sqrt_ratio_at_tick(0)
        liquidity = 1000000
        amount_out = 5
        zero_for_one = True

        # Test with valid inputs
        result = SqrtPriceMath.get_next_sqrt_price_from_output(sqrt_p_x96, liquidity, amount_out, zero_for_one)
        self.assertIsNotNone(result)

        # Test with zero_for_one = False
        result = SqrtPriceMath.get_next_sqrt_price_from_output(sqrt_p_x96, liquidity, amount_out, False)
        self.assertIsNotNone(result)

    def test_get_amount0_delta_unsigned(self):
        sqrt_ratio_a_x96 = 10
        sqrt_ratio_b_x96 = 20
        liquidity = 1000
        round_up = True

        # Test with valid inputs
        result = SqrtPriceMath.get_amount0_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, round_up)
        self.assertIsNotNone(result)

        # Test with round_up = False
        result = SqrtPriceMath.get_amount0_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, False)
        self.assertIsNotNone(result)

    def test_get_amount1_delta_unsigned(self):
        sqrt_ratio_a_x96 = 10
        sqrt_ratio_b_x96 = 20
        liquidity = 1000
        round_up = True

        # Test with valid inputs
        result = SqrtPriceMath.get_amount1_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, round_up)
        self.assertIsNotNone(result)

        # Test with round_up = False
        result = SqrtPriceMath.get_amount1_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, False)
        self.assertIsNotNone(result)

    def test_get_amount0_delta_signed(self):
        sqrt_ratio_a_x96 = 10
        sqrt_ratio_b_x96 = 20
        liquidity = 1000

        # Test with positive liquidity
        result = SqrtPriceMath.get_amount0_delta_signed(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity)
        self.assertIsNotNone(result)

        # Test with negative liquidity
        result = SqrtPriceMath.get_amount0_delta_signed(sqrt_ratio_a_x96, sqrt_ratio_b_x96, -liquidity)
        self.assertIsNotNone(result)

    def test_get_amount1_delta_signed(self):
        sqrt_ratio_a_x96 = 10
        sqrt_ratio_b_x96 = 20
        liquidity = 1000

        # Test with positive liquidity
        result = SqrtPriceMath.get_amount1_delta_signed(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity)
        self.assertIsNotNone(result)

        # Test with negative liquidity
        result = SqrtPriceMath.get_amount1_delta_signed(sqrt_ratio_a_x96, sqrt_ratio_b_x96, -liquidity)
        self.assertIsNotNone(result)


class TestTickMath(unittest.TestCase):
    def test_get_sqrt_ratio_at_tick(self):
        # Test with tick = MIN_TICK
        result = TickMath.get_sqrt_ratio_at_tick(TickMath.MIN_TICK)
        self.assertEqual(result, TickMath.MIN_SQRT_RATIO)

        # Test with tick = MAX_TICK
        result = TickMath.get_sqrt_ratio_at_tick(TickMath.MAX_TICK)
        self.assertEqual(result, TickMath.MAX_SQRT_RATIO)

        # Test with tick = 0
        result = TickMath.get_sqrt_ratio_at_tick(0)
        self.assertAlmostEqual(result / 2**96, 1.0)

        # Test with tick = 100
        result = TickMath.get_sqrt_ratio_at_tick(100)
        self.assertAlmostEqual(result / 2**96, (TickMath.TICK_BASE**100) ** 0.5)

        # Test with tick > MAX_TICK, should raise an AssertionError
        with self.assertRaises(AssertionError):
            TickMath.get_sqrt_ratio_at_tick(TickMath.MAX_TICK + 1)

        # Test with tick < MIN_TICK, should raise an AssertionError
        with self.assertRaises(AssertionError):
            TickMath.get_sqrt_ratio_at_tick(TickMath.MIN_TICK - 1)

    def test_get_tick_at_sqrt_ratio(self):
        # Test with sqrtPriceX96 = MIN_SQRT_RATIO
        result = TickMath.get_tick_at_sqrt_ratio(TickMath.MIN_SQRT_RATIO)
        self.assertIsNotNone(result)

        # Test with sqrtPriceX96 = MAX_SQRT_RATIO - 1
        result = TickMath.get_tick_at_sqrt_ratio(TickMath.MAX_SQRT_RATIO - 1)
        self.assertIsNotNone(result)

        # Test with sqrtPriceX96 < MIN_SQRT_RATIO, should raise an AssertionError
        with self.assertRaises(AssertionError):
            TickMath.get_tick_at_sqrt_ratio(TickMath.MIN_SQRT_RATIO - 1)

        # Test with sqrtPriceX96 >= MAX_SQRT_RATIO, should raise an AssertionError
        with self.assertRaises(AssertionError):
            TickMath.get_tick_at_sqrt_ratio(TickMath.MAX_SQRT_RATIO)

    def test_tick_to_price(self):
        assert TickMath.tick_to_price(82_164, 0, 0) == pytest.approx(3_699.634, abs=0.001)
        assert TickMath.tick_to_price(82_165, 0, 0) == pytest.approx(3_700.004, abs=0.001)
        assert TickMath.tick_to_price(83_667, 0, 0) == pytest.approx(4_299.619, abs=0.001)
        assert TickMath.tick_to_price(83_668, 0, 0) == pytest.approx(4_300.049, abs=0.001)

    def test_price_to_tick(self):
        assert TickMath.price_to_tick(3_699.635, 0, 0) == 82_164
        assert TickMath.price_to_tick(3_700.000, 0, 0) == 82_164
        assert TickMath.price_to_tick(3_700.005, 0, 0) == 82_165
        assert TickMath.price_to_tick(4_299.620, 0, 0) == 83_667
        assert TickMath.price_to_tick(4_300.000, 0, 0) == 83_667
        assert TickMath.price_to_tick(4_300.050, 0, 0) == 83_668

    def test_next_tick(self):
        sqrt_price_ratio_x96 = TickMath.get_sqrt_ratio_at_tick(0)
        assert TickMath.get_tick_at_sqrt_ratio(sqrt_price_ratio_x96) == 0
        assert TickMath.get_tick_at_sqrt_ratio(sqrt_price_ratio_x96 - 1) == -1

    def test_sqrt_price_x96_to_sqrt_price(self):
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_sqrt_price(2**96, 18, 18), 1.0, places=5)
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_sqrt_price(2**96, 18, 6), 1000000.0, places=5)
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_sqrt_price(2**96, 6, 18), 0.000001, places=5)

    def test_sqrt_price_x96_to_price(self):
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_price(2**96, 18, 18), 1.0, places=5)
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_price(2**96, 18, 6), 1000000.0**2, places=5)
        self.assertAlmostEqual(TickMath.sqrt_price_x96_to_price(2**96, 6, 18), 0.000001**2, places=5)


class TestSwapMath(unittest.TestCase):
    def test_compute_swap_step(self):
        sqrt_ratio_current_x96 = 1
        sqrt_ratio_target_x96 = 2
        liquidity = 1000
        amount_remaining = 500
        fee_pips = 10

        # Test with exact_in = True
        result = SwapMath.compute_swap_step(
            sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, amount_remaining, fee_pips
        )
        self.assertIsNotNone(result)

        # Test with exact_in = False
        result = SwapMath.compute_swap_step(
            sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, -amount_remaining, fee_pips
        )
        self.assertIsNotNone(result)


if __name__ == "__main__":
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestTickMath("test_next_tick"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
