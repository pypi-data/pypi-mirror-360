# https://github.com/compound-finance/compound-protocol/blob/master/contracts/ExponentialNoError.sol
from dataclasses import dataclass

EXPSCALE: int = 10**18


@dataclass
class Exp:
    mantissa: int


def truncate(x: Exp) -> int:
    """
    Truncates the given x to a whole number value
    :param x:
    :return:
    """
    return x.mantissa // EXPSCALE


def mul_scalar_truncate(a: Exp, scalar: int) -> int:
    product = mul_exp_int(a, scalar)
    return truncate(product)


def mul_scalar_truncate_add_int(a: Exp, scalar: int, addend: int) -> int:
    product = mul_exp_int(a, scalar)
    return truncate(product) + addend


def add_exp(a: Exp, b: Exp) -> Exp:
    return Exp(a.mantissa + b.mantissa)


def sub_exp(a: Exp, b: Exp) -> Exp:
    return Exp(a.mantissa - b.mantissa)


def mul_exp(a: Exp, b: Exp) -> Exp:
    return Exp(a.mantissa * b.mantissa // EXPSCALE)


def mul_exp_int(a: Exp, b: int) -> Exp:
    return Exp(a.mantissa * b)


def mul_int_exp(a: int, b: Exp) -> int:
    return a * b.mantissa // EXPSCALE


def div_exp(a: Exp, b: Exp) -> Exp:
    return Exp(a.mantissa * EXPSCALE // b.mantissa)


def div_exp_int(a: Exp, b: int) -> Exp:
    return Exp(a.mantissa // b)


def div_int_exp(a: int, b: Exp) -> int:
    return a * EXPSCALE // b.mantissa
