class UnsafeMath:
    @staticmethod
    def div_rounding_up(x: int, y: int) -> int:
        assert y != 0, "division by zero is undefined"
        return (x // y) + (x % y > 0)
