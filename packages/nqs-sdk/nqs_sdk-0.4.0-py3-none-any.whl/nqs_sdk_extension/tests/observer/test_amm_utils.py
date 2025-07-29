# type: ignore
import unittest

from nqs_sdk_extension.observer.protocol.amm_utils import uniswap_v3_il


class TestUniswapV3Utils(unittest.TestCase):
    def test_uniwap_v3_il_in_range(self):
        minimum_range = 0.9
        maximum_range = 1.1
        initial_price = 1.0
        liquidity = 1000

        _, abs_il_0, value_0 = uniswap_v3_il(minimum_range, maximum_range, initial_price, 1.0, liquidity)
        _, abs_il_1, value_1 = uniswap_v3_il(minimum_range, maximum_range, initial_price, 1.10, liquidity)
        _, abs_il_2, value_2 = uniswap_v3_il(minimum_range, maximum_range, initial_price, 1.20, liquidity)

        self.assertAlmostEqual(abs_il_0, 0.0)
        self.assertGreater(abs_il_1, abs_il_2)  # TODO: make it more precise

    def test_uniwap_v3_il_out_of_range(self):
        minimum_range = 0.9
        maximum_range = 0.95
        initial_price = 1.0
        liquidity = 1000

        _, abs_il_1, value_1 = uniswap_v3_il(minimum_range, maximum_range, initial_price, 1.10, liquidity)
        _, abs_il_2, value_2 = uniswap_v3_il(minimum_range, maximum_range, initial_price, 1.20, liquidity)

        self.assertAlmostEqual(abs_il_1, 0.0)
        self.assertAlmostEqual(abs_il_2, 0.0)
        self.assertAlmostEqual(value_1, value_2)


# run the tests
if __name__ == "__main__":
    unittest.main()
