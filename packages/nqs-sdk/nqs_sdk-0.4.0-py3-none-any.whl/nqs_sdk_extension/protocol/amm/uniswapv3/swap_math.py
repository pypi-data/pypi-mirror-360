from typing import Tuple

from .full_math import FullMath
from .sqrt_price_math import SqrtPriceMath

# https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/SwapMath.sol


class SwapMath:
    @staticmethod
    def compute_swap_step(
        sqrt_ratio_current_x96: int, sqrt_ratio_target_x96: int, liquidity: int, amount_remaining: int, fee_pips: int
    ) -> Tuple[int, int, int, int]:
        zero_for_one = sqrt_ratio_current_x96 >= sqrt_ratio_target_x96
        exact_in = amount_remaining >= 0

        if exact_in:
            amount_remaining_less_fee = FullMath.mul_div(amount_remaining, 1_000_000 - fee_pips, 1_000_000)
            amount_in = (
                SqrtPriceMath.get_amount0_delta_unsigned(sqrt_ratio_target_x96, sqrt_ratio_current_x96, liquidity, True)
                if zero_for_one
                else SqrtPriceMath.get_amount1_delta_unsigned(
                    sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, True
                )
            )
            sqrt_ratio_next_x96 = (
                sqrt_ratio_target_x96
                if amount_remaining_less_fee >= amount_in
                else SqrtPriceMath.get_next_sqrt_price_from_input(
                    sqrt_ratio_current_x96, liquidity, amount_remaining_less_fee, zero_for_one
                )
            )
        else:
            amount_out = (
                SqrtPriceMath.get_amount1_delta_unsigned(
                    sqrt_ratio_target_x96, sqrt_ratio_current_x96, liquidity, False
                )
                if zero_for_one
                else SqrtPriceMath.get_amount0_delta_unsigned(
                    sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, False
                )
            )
            sqrt_ratio_next_x96 = (
                sqrt_ratio_target_x96
                if -amount_remaining >= amount_out
                else SqrtPriceMath.get_next_sqrt_price_from_output(
                    sqrt_ratio_current_x96, liquidity, -amount_remaining, zero_for_one
                )
            )
        max = sqrt_ratio_target_x96 == sqrt_ratio_next_x96

        if zero_for_one:
            amount_in = (
                amount_in
                if max and exact_in
                else SqrtPriceMath.get_amount0_delta_unsigned(
                    sqrt_ratio_next_x96, sqrt_ratio_current_x96, liquidity, True
                )
            )
            amount_out = (
                amount_out
                if max and not exact_in
                else SqrtPriceMath.get_amount1_delta_unsigned(
                    sqrt_ratio_next_x96, sqrt_ratio_current_x96, liquidity, False
                )
            )
        else:
            amount_in = (
                amount_in
                if max and exact_in
                else SqrtPriceMath.get_amount1_delta_unsigned(
                    sqrt_ratio_current_x96, sqrt_ratio_next_x96, liquidity, True
                )
            )
            amount_out = (
                amount_out
                if max and not exact_in
                else SqrtPriceMath.get_amount0_delta_unsigned(
                    sqrt_ratio_current_x96, sqrt_ratio_next_x96, liquidity, False
                )
            )

        if not exact_in and amount_out > -amount_remaining:
            amount_out = -amount_remaining

        if exact_in and sqrt_ratio_next_x96 != sqrt_ratio_target_x96:
            fee_amount = amount_remaining - amount_in
        else:
            fee_amount = FullMath.mul_div_rounding_up(amount_in, fee_pips, 1_000_000 - fee_pips)

        return sqrt_ratio_next_x96, amount_in, amount_out, fee_amount
