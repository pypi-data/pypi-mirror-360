from abc import abstractmethod
from typing import Any, Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.spot.spot_process import SpotProcess


class StochasticProcess(SpotProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: Any):
        super().__init__(pair, kwargs["current_timestamp"])
        self.calibrate: bool = kwargs.get("calibrate", False)

    @abstractmethod
    def evolve(self, dt: float, dw: float, next_timestamp: int) -> None:
        """
        Evolves the process from the current time self.t0 to the next
        :param dt: delta time
        :param dw: the necessary brownian motion increment
        :param next_timestamp: the timestamp after the evolve action has been executed
        :return:
        """
        pass

    def calibrate_params(self, spot_ts: NDArray[np.float64]) -> None:
        """
        Calibrate the parameters of the spot process
        :param spot_ts: the spot path used to calibrate the parameters
        :return:
        """
        pass

    def get_spot(self, timestamp: int) -> float:
        """
        Returns the spot value at the current time
        :param timestamp: the current time
        :return: the spot value
        """
        if self.current_timestamp == timestamp:
            return self.s0
        else:
            raise ValueError(
                f"It is not possible to get the spot value at timestamp {timestamp} process {self.pair}. The last"
                f"known value for the process is at timestamp {self.current_timestamp}"
            )
