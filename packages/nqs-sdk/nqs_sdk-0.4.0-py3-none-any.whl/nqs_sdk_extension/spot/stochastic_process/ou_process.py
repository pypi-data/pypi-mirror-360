from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.spot.stochastic_process.stochastic_process import StochasticProcess


class OUProcess(StochasticProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: float):
        super().__init__(pair, **kwargs)
        self.s0 = kwargs["s0"]
        self._mean_reversion = kwargs["mean_reversion"]
        self._mean = kwargs["mean"]
        self._vol = kwargs["vol"]

    def calibrate_params(self, spot_ts: NDArray[np.float64]) -> None:
        """
        Calibrate the parameters of the spot process
        :param spot_ts: the spot path used to calibrate the parameters
        :return:
        """
        raise NotImplementedError("Not implemented for OUProcess")

    def evolve(self, dt: float, dw: float, next_timestamp: int) -> None:
        """
        Evolves the process from the current time self.t0 to the next
        :param dt: delta time
        :param dw: the necessary brownian motion increment
        :param next_timestamp: the timestamp after the evolve action has been executed
        :return:
        """
        self.s0 += self._mean_reversion * (self._mean - self.s0) * dt + self._vol * np.sqrt(dt) * dw
        self.current_timestamp = next_timestamp
