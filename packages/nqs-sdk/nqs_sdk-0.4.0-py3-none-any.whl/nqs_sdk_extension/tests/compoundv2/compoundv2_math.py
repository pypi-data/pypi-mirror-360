# type: ignore

import unittest

from nqs_sdk_extension.protocol.lending_protocol.compoundv2.full_math import Exp, mul_exp, mul_scalar_truncate


class TestCompoundMath(unittest.TestCase):
    def test_mul_scalar_truncate(self):
        a = 10**18
        b = 20

        # Test with valid inputs
        result = mul_scalar_truncate(Exp(a), b)
        self.assertEqual(result, 20)

    def test_mul_scalar_truncate_add_int(self):
        a = 10**18
        b = 20
        c = 10

        # Test with valid inputs
        result = mul_scalar_truncate(Exp(a), b, c)
        self.assertEqual(result, 30)

    def test_mul_exp(self):
        a = 10**18
        b = 2 * 10**18

        result = mul_exp(Exp(a), Exp(b))
        self.assertEqual(result, Exp(20 * 10**18))


if __name__ == "__main__":
    unittest.main()
