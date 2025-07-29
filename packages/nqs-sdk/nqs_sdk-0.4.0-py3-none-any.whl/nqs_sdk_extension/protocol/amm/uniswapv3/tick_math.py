import math

import numpy as np

"""
Inline assembly allows you to write low-level EVM (Ethereum Virtual Machine) code within Solidity,
which can be useful for optimizing certain parts of your code.

However, Python doesn't have a direct equivalent to Solidity's inline assembly.
Python is a high-level language and doesn't provide low-level access to memory or CPU instructions.
Therefore, translating this function directly into Python is not feasible.

The function `get_tick_at_sqrt_ratio` is performing a binary search to find the most significant bit (MSB) of the ratio,
then it calculates the logarithm base 2 of the ratio, and finally it calculates the tick (price)
corresponding to the given square root price.
"""

# XXX: THIS IS AN APPROXIMATION OF THE SOLIDITY CODE, NOT THE EXACT TRANSLATION


class TickMath:
    """
    sqrt_price_x96 = math.sqrt(1.0001 ** tick) * 2**96
    url: https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol
    """

    TICK_BASE = 1.0001
    TICK_SPACING = 1  # XXX not other values are supported yet / should be a quick-fix
    MIN_TICK = -887272
    MAX_TICK = -MIN_TICK

    # Python float (for self-consistency)
    MIN_SQRT_RATIO = 4295128738
    MAX_SQRT_RATIO = 1461446703478072065887575149053462049098722967552

    # SOLDITY
    # MIN_SQRT_RATIO = 4295128739
    # MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342

    # Use the following constants for efficient computation
    LOG_TICK_BASE_HALF = math.log(1.0001) / 2
    LOG_2 = math.log(2)

    @staticmethod
    def sqrt_price_x96_to_sqrt_price(sqrt_price_x96: int, decimal0: int, decimal1: int) -> float:
        # NOT IN THE SMART-CONTRACT
        return float(sqrt_price_x96 / 2**96 * 10 ** (0.5 * (decimal0 - decimal1)))

    @staticmethod
    def sqrt_price_x96_to_price(sqrt_price_x96: int, decimal0: int, decimal1: int) -> float:
        # NOT IN THE SMART-CONTRACT
        return TickMath.sqrt_price_x96_to_sqrt_price(sqrt_price_x96, decimal0, decimal1) ** 2

    @staticmethod
    def price_to_sqrt_price_x96(price: float, decimal0: int, decimal1: int) -> int:
        # NOT IN THE SMART-CONTRACT
        return int((price**0.5) * 2**96 / 10 ** (0.5 * (decimal0 - decimal1)))

    @staticmethod
    def tick_to_price(tick: int, decimal0: int, decimal1: int) -> float:
        # NOT IN THE SMART-CONTRACT
        # equation 6.1
        return float(TickMath.TICK_BASE**tick * 10 ** (decimal0 - decimal1))

    @staticmethod
    def price_to_tick(price: float, decimal0: int, decimal1: int) -> int:
        # NOT IN THE SMART-CONTRACT
        # equation X.X
        return int(np.floor(np.emath.logn(TickMath.TICK_BASE, price / 10 ** (decimal0 - decimal1))))

    @staticmethod
    def get_sqrt_ratio_at_tick(tick: int) -> int:
        # Get the absolute value of the tick
        abs_tick = abs(tick)

        # Ensure the absolute tick is less than or equal to the maximum tick
        assert abs_tick <= TickMath.MAX_TICK, "T"

        # Pythonic calculation
        sqrt_price_x96 = math.exp(TickMath.LOG_TICK_BASE_HALF * tick + TickMath.LOG_2 * 96)
        sqrt_price_x96 = int(sqrt_price_x96)  # round down
        return sqrt_price_x96

    @staticmethod
    def get_tick_at_sqrt_ratio(sqrt_price_x96: int) -> int:
        # Ensure the input is within the valid range
        assert sqrt_price_x96 >= TickMath.MIN_SQRT_RATIO and sqrt_price_x96 < TickMath.MAX_SQRT_RATIO, "R"

        tick = (math.log(sqrt_price_x96) - TickMath.LOG_2 * 96) / TickMath.LOG_TICK_BASE_HALF
        tick = int(tick)  # round down

        # quickfix for the rounding error
        sqrt_price_x96_at_tick = TickMath.get_sqrt_ratio_at_tick(tick)
        if sqrt_price_x96_at_tick > sqrt_price_x96:
            tick -= 1
        if TickMath.get_sqrt_ratio_at_tick(tick + 1) < sqrt_price_x96:
            tick += 1
        return tick

    """
    @staticmethod
    def get_sqrt_ratio_at_tick(tick):
        # Get the absolute value of the tick
        abs_tick = abs(tick)

        # Ensure the absolute tick is less than or equal to the maximum tick
        assert abs_tick <= TickMath.MAX_TICK, 'T'

        # Initialize the ratio based on the least significant bit of the absolute tick
        ratio = 0xfffcb933bd6fad37aa2d162d1a594001 if abs_tick & 0x1 != 0 else 0x100000000000000000000000000000000

        # Precomputed ratios for each bit
        ratios = [
            0xfff97272373d413259a46990580e213a,
            0xfff2e50f5f656932ef12357cf3c7fdcc,
            0xffe5caca7e10e4e61c3624eaa0941cd0,
            0xffcb9843d60f6159c9db58835c926644,
            0xff973b41fa98c081472e6896dfb254c0,
            0xff2ea16466c96a3843ec78b326b52861,
            0xfe5dee046a99a2a811c461f1969c3053,
            0xfcbe86c7900a88aedcffc83b479aa3a4,
            0xf987a7253ac413176f2b074cf7815e54,
            0xf3392b0822b70005940c7a398e4b70f3,
            0xe7159475a2c29b7443b29c7fa6e889d9,
            0xd097f3bdfd2022b8845ad8f792aa5825,
            0xa9f746462d870fdf8a65dc1f90e061e5,
            0x70d869a156d2a1b890bb3df62baf32f7,
            0x31be135f97d08fd981231505542fcfa6,
            0x9aa508b5b7a84e1c677de54f3e99bc9,
            0x5d6af8dedb81196699c329225ee604,
            0x2216e584f5fa1ea926041bedfe98,
            0x48a170391f7dc42444e8fa2
        ]

        # For each bit in the absolute tick
        for i in range(1, 20):
            # If the bit is set
            if abs_tick & (1 << i) != 0:
                # Multiply the ratio by the corresponding precomputed ratio and shift right by 128
                ratio = (ratio * ratios[i-1]) >> 128

        # If the tick is positive
        if tick > 0:
            # Invert the ratio
            ratio = ((1 << 256) - 1) // ratio # do not forget the parenthisis..

        # Calculate the square root price, rounding up if necessary
        sqrt_price_x96 = (ratio >> 32) + (1 if ratio % (1 << 32) != 0 else 0)

        # Return the square root price
        return sqrt_price_x96

    @staticmethod
    def get_tick_at_sqrt_ratio(sqrt_price_x96):

        # Ensure the input is within the valid range
        assert sqrt_price_x96 >= TickMath.MIN_SQRT_RATIO and sqrt_price_x96 < TickMath.MAX_SQRT_RATIO, 'R'

        # Shift the input to the left by 32 bits
        ratio = sqrt_price_x96 << 32

        # Find the most significant bit of the ratio
        msb = math.floor(math.log2(ratio))
        print(msb)

        # Adjust the ratio based on the most significant bit
        if msb >= 128:
            r = ratio >> (msb - 127)
        else:
            r = ratio << (127 - msb)

        # Calculate the logarithm of the ratio
        log_2 = (msb - 128) << 64

        # Refine the logarithm calculation
        for i in range(127, 50, -1):
            r = (r * r) >> 127
            if r >= (1 << 128):
                r = r >> 1
                log_2 = log_2 | (1 << (i - 1))

        # Multiply the logarithm by a constant
        log_sqrt10001 = log_2 * 255738958999603826347141  # 128.128 number

        # Calculate the lower and upper bounds of the tick
        tickLow = int((log_sqrt10001 - 3402992956809132418596140100660247210) >> 128)
        tickHi = int((log_sqrt10001 + 291339464771989622907027621153398088495) >> 128)

        # Determine the tick based on the lower and upper bounds
        if tickLow == tickHi:
            tick = tickLow
        else:
            print(tickLow, tickHi, sqrt_price_x96)
            tick = tickHi if TickMath.get_sqrt_ratio_at_tick(tickHi) <= sqrt_price_x96 else tickLow

        return tick
    """
