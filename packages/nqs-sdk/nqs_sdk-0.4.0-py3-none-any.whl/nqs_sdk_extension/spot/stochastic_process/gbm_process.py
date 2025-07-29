from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.spot.stochastic_process.stochastic_process import StochasticProcess
from nqs_sdk_extension.spot.utils import drift, volatility


class GBMProcess(StochasticProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: float):
        super().__init__(pair, **kwargs)
        self.s0 = kwargs.get("s0", -1)  # optional in case of calibrated process
        self._mu = kwargs.get("mu", -1000)  # optional in case of calibrated process
        self._vol = kwargs.get("vol", -1)  # optional in case of calibrated process
        self._validate()

    def _validate(self) -> None:
        if not self.calibrate:
            if self.s0 == -1 or self._mu == -1000 or self._vol == -1:
                raise ValueError(
                    f"The pair {self.pair} is not calibrated. Therefore if a GBM dynamics is chosen "
                    f"s0, mu and vol must be provided."
                )
            if self._vol < 0:
                raise ValueError(f"Invalid volatility value: vol={self._vol}. vol must be positive or 0.")

    def calibrate_params(self, spot_ts: NDArray[np.float64]) -> None:
        """
        Calibrate the parameters of the spot process
        :param spot_ts: the spot path used to calibrate the parameters
        :return:
        """
        self.s0 = spot_ts[0]
        mu = drift(spot_ts)[0]
        vol = volatility(spot_ts, len(spot_ts))[-1]
        self._mu = mu / 100.0
        self._vol = float(vol) / 100.0

    def evolve(self, dt: float, dw: float, next_timestamp: int) -> None:
        """
        Evolves the process from the current time self.t0 to the next
        :param dt: delta time
        :param dw: the necessary brownian motion increment
        :param next_timestamp: the timestamp after the evolve action has been executed
        :return:
        """
        if dt > 0 and next_timestamp == self.current_timestamp:
            raise ValueError(
                "Inconsistency between the delta time dt>0 and the next timestamp being equal to "
                "the current timestamp"
            )
        self.s0 *= np.exp((self._mu - 0.5 * self._vol**2) * dt + self._vol * np.sqrt(dt) * dw)
        self.current_timestamp = next_timestamp
