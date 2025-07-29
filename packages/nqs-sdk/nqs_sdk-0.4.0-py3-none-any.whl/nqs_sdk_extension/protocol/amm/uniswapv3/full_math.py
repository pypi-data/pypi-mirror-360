# https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/FullMath.sol


class FullMath:
    """
    url: https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/FullMath.sol
    """

    # pythonic version
    @staticmethod
    def mul_div(a: int, b: int, denominator: int) -> int:
        assert denominator > 0
        return (a * b) // denominator

    """
    # solidity version, translated to python but not passing all the tests
    @staticmethod
    def mul_div(a, b, denominator):
        # 512-bit multiply [prod1 prod0] = a * b
        prod0 = a * b  # Least significant 256 bits of the product
        prod1 = ((a * b) >> 256)  # Most significant 256 bits of the product

        # Handle non-overflow cases, 256 by 256 division
        if prod1 == 0:
            assert denominator > 0
            result = prod0 // denominator
            return result

        # Make sure the result is less than 2**256.
        # Also prevents denominator == 0
        assert denominator > prod1

        # 512 by 256 division.
        remainder = (a * b) % denominator
        prod0 -= remainder
        prod1 -= (remainder > prod0)

        # Factor powers of two out of denominator
        twos = -denominator & denominator
        denominator //= twos
        prod0 //= twos
        twos = ((~twos) // twos) + 1
        prod0 |= prod1 * twos

        # Invert denominator mod 2**256
        inv = (3 * denominator) ** 2
        for _ in range(6):
            inv *= 2 - denominator * inv

        result = prod0 * inv
        return result
    """

    # not passing the uint256 max test
    @staticmethod
    def mul_div_rounding_up(a: int, b: int, denominator: int) -> int:
        result = FullMath.mul_div(a, b, denominator)
        if (a * b) % denominator > 0:
            # require(result < type(uint256).max); NOT TESTED HERE
            result += 1
        return result
