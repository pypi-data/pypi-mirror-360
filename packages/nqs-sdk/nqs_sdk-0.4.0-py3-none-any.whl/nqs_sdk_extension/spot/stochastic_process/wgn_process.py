from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.spot.stochastic_process.stochastic_process import StochasticProcess
from nqs_sdk_extension.spot.utils import volatility


class WGNProcess(StochasticProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: float):
        super().__init__(pair, **kwargs)
        self.s0 = kwargs.get("s0", -1)  # optional in case of calibrated process
        self._mean = kwargs.get("s0", -1)  # used to store the initial value
        self._vol = kwargs.get("vol", -1)  # optional in case of calibrated process
        self._validate()

    def _validate(self) -> None:
        if not self.calibrate:
            if self.s0 == -1 or self._mean == -1 or self._vol == -1:
                raise ValueError(
                    f"The pair {self.pair} is not calibrated. Therefore if a WGN dynamics is chosen"
                    f"s0, mean and vol must be provided."
                )

    def calibrate_params(self, spot_ts: NDArray[np.float64]) -> None:
        """
        Calibrate the parameters of the spot process
        :param spot_ts: the spot path used to calibrate the parameters
        :return:
        """
        # Calibrate s0
        self.s0 = spot_ts[0]
        self._mean = spot_ts[0]
        # Calibrate vol
        vol = volatility(spot_ts, len(spot_ts))[-1] / np.sqrt(2)
        self._vol = float(vol) / 100.0

    def evolve(self, dt: float, dw: float, next_timestamp: int) -> None:
        """
        Evolves the process from the current time self.t0 to the next
        :param dt: delta time
        :param dw: the necessary brownian motion increment
        :param next_timestamp: the timestamp after the evolve action has been executed
        :return:
        """
        self.s0 = self._mean * (1 + self._vol * dw)
        self.current_timestamp = next_timestamp
