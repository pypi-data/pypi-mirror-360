import datetime

from nqs_pycore import quantlib


class BlockNumberOrTimestamp:
    @staticmethod
    def block_number(n: int) -> "quantlib.BlockNumberOrTimestamp":
        pycore_obj = quantlib.BlockNumberOrTimestamp.block_number(n)

        return pycore_obj

    @staticmethod
    def timestamp(t: int) -> "quantlib.BlockNumberOrTimestamp":
        dt = datetime.datetime.fromtimestamp(t, tz=datetime.timezone.utc)

        pycore_obj = quantlib.BlockNumberOrTimestamp.timestamp(dt)

        return pycore_obj
