from .fixed_point_96 import FixedPoint96
from .full_math import FullMath
from .unsafe_math import UnsafeMath

# https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/SqrtPriceMath.sol


class SqrtPriceMath:
    @staticmethod
    def get_next_sqrt_price_from_amount0_rounding_up(sqrt_p_x96: int, liquidity: int, amount: int, add: bool) -> int:
        if amount == 0:
            return sqrt_p_x96
        numerator1 = liquidity << FixedPoint96.RESOLUTION
        if add:
            product = amount * sqrt_p_x96
            if product // amount == sqrt_p_x96:
                denominator = numerator1 + product
                if denominator >= numerator1:
                    return FullMath.mul_div_rounding_up(numerator1, sqrt_p_x96, denominator)
            return UnsafeMath.div_rounding_up(numerator1, (numerator1 // sqrt_p_x96) + amount)
        else:
            product = amount * sqrt_p_x96
            if product // amount == sqrt_p_x96 and numerator1 > product:
                denominator = numerator1 - product
                return FullMath.mul_div_rounding_up(numerator1, sqrt_p_x96, denominator)
        return 0

    @staticmethod
    def get_next_sqrt_price_from_amount1_rounding_down(sqrt_p_x96: int, liquidity: int, amount: int, add: bool) -> int:
        amount = int(amount)
        if add:
            quotient = (
                ((amount << FixedPoint96.RESOLUTION) // liquidity)
                if amount <= (1 << 160) - 1
                else FullMath.mul_div(amount, FixedPoint96.Q96, liquidity)
            )
            return sqrt_p_x96 + quotient
        else:
            quotient = (
                UnsafeMath.div_rounding_up(amount << FixedPoint96.RESOLUTION, liquidity)
                if amount <= (1 << 160) - 1
                else FullMath.mul_div_rounding_up(amount, FixedPoint96.Q96, liquidity)
            )
            assert sqrt_p_x96 > quotient
            return sqrt_p_x96 - quotient

    @staticmethod
    def get_next_sqrt_price_from_input(sqrt_p_x96: int, liquidity: int, amount_in: int, zero_for_one: bool) -> int:
        assert sqrt_p_x96 > 0
        assert liquidity > 0

        if zero_for_one:
            return SqrtPriceMath.get_next_sqrt_price_from_amount0_rounding_up(sqrt_p_x96, liquidity, amount_in, True)
        else:
            return SqrtPriceMath.get_next_sqrt_price_from_amount1_rounding_down(sqrt_p_x96, liquidity, amount_in, True)

    @staticmethod
    def get_next_sqrt_price_from_output(sqrt_p_x96: int, liquidity: int, amount_out: int, zero_for_one: bool) -> int:
        assert sqrt_p_x96 > 0
        assert liquidity > 0

        if zero_for_one:
            return SqrtPriceMath.get_next_sqrt_price_from_amount1_rounding_down(
                sqrt_p_x96, liquidity, amount_out, False
            )
        else:
            return SqrtPriceMath.get_next_sqrt_price_from_amount0_rounding_up(sqrt_p_x96, liquidity, amount_out, False)

    @staticmethod
    def get_amount0_delta_unsigned(sqrt_ratio_a_x96: int, sqrt_ratio_b_x96: int, liquidity: int, round_up: bool) -> int:
        if sqrt_ratio_a_x96 > sqrt_ratio_b_x96:
            sqrt_ratio_a_x96, sqrt_ratio_b_x96 = sqrt_ratio_b_x96, sqrt_ratio_a_x96

        numerator1 = liquidity << FixedPoint96.RESOLUTION
        numerator2 = sqrt_ratio_b_x96 - sqrt_ratio_a_x96

        assert sqrt_ratio_a_x96 > 0

        if round_up:
            return UnsafeMath.div_rounding_up(
                FullMath.mul_div_rounding_up(numerator1, numerator2, sqrt_ratio_b_x96), sqrt_ratio_a_x96
            )
        else:
            return FullMath.mul_div(numerator1, numerator2, sqrt_ratio_b_x96) // sqrt_ratio_a_x96

    @staticmethod
    def get_amount1_delta_unsigned(sqrt_ratio_a_x96: int, sqrt_ratio_b_x96: int, liquidity: int, round_up: bool) -> int:
        if sqrt_ratio_a_x96 > sqrt_ratio_b_x96:
            sqrt_ratio_a_x96, sqrt_ratio_b_x96 = sqrt_ratio_b_x96, sqrt_ratio_a_x96

        if round_up:
            return FullMath.mul_div_rounding_up(liquidity, sqrt_ratio_b_x96 - sqrt_ratio_a_x96, FixedPoint96.Q96)
        else:
            return FullMath.mul_div(liquidity, sqrt_ratio_b_x96 - sqrt_ratio_a_x96, FixedPoint96.Q96)

    @staticmethod
    def get_amount0_delta_signed(sqrt_ratio_a_x96: int, sqrt_ratio_b_x96: int, liquidity: int) -> int:
        if liquidity < 0:
            return -SqrtPriceMath.get_amount0_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, -liquidity, False)
        else:
            return SqrtPriceMath.get_amount0_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, True)

    @staticmethod
    def get_amount1_delta_signed(sqrt_ratio_a_x96: int, sqrt_ratio_b_x96: int, liquidity: int) -> int:
        if liquidity < 0:
            return -SqrtPriceMath.get_amount1_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, -liquidity, False)
        else:
            return SqrtPriceMath.get_amount1_delta_unsigned(sqrt_ratio_a_x96, sqrt_ratio_b_x96, liquidity, True)
