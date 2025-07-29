import logging
from typing import Any, Optional, Tuple

import numpy as np
import numpy.typing as npt

from nqs_sdk_extension.spot.spot_process import SpotProcess


class CustomProcess(SpotProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: Any):
        super().__init__(pair, kwargs["current_timestamp"])
        self.simulation_end_timestamp = kwargs["end_timestamp"]
        self._timestamps = kwargs["timestamps"]
        self._path = kwargs["path"]
        self._validate()
        self.s0 = self._path[0]

    def get_token_address(self, token: str) -> str:
        raise NotImplementedError("Not implemented for CustomSpots")

    def get_historical_spot_value(self, datetime: np.str_ | str) -> float:
        raise NotImplementedError("Not implemented for CustomSpots")

    def get_historical_path(
        self, begin: int, limit: int, end: Optional[int] = None
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.int64]]:
        raise NotImplementedError("Not implemented for CustomSpots")

    def _validate(self, path_id: int = 0) -> None:
        """
        Safety checks on the custom spots
        :param path_id: the path_id for logging purposes
        :return:
        """
        assert len(self._timestamps) == len(self._path), (
            "For custom spots, the 'timestamps' series and 'path' series must " "have same length."
        )
        assert (
            min(self._timestamps) == self.current_timestamp
        ), f"Custom Spots - 'timestamp' series must start at {self.current_timestamp}"
        if max(self._timestamps) > self.simulation_end_timestamp:
            logging.warning(
                f"path_id:{path_id} - Custom Spot - For custom spot {self.pair}, the provided timestamps "
                f"end later (t={max(self._timestamps)}) than the simulation last timestamp "
                f"(t={self.simulation_end_timestamp}). The price timeseries will be truncated after the "
                f"simulation end timestamp."
            )
        elif max(self._timestamps) < self.simulation_end_timestamp:
            logging.warning(
                f"path_id:{path_id} - Custom Spot - For custom spot {self.pair}, the provided timestamps end "
                f"earlier (t={max(self._timestamps)}) than the simulation end timestamp "
                f"(t={self.simulation_end_timestamp}). The price timeseries will be constant equal to the last "
                f"provided value "
                f"until the end of the simulation."
            )

    def get_spot(self, timestamp: int) -> float:
        """
        Returns the spot value at the current time
        :param timestamp: the current timestamp
        :return: the spot value
        """
        # Find the index of the closest time step less than or equal to t
        idx = np.searchsorted(self._timestamps, timestamp, side="right") - 1
        # Make sure the index is within the valid range
        idx = np.clip(idx, 0, len(self._timestamps) - 2)
        # Calculate the interpolation weight
        weight = (timestamp - self._timestamps[idx]) / (self._timestamps[idx + 1] - self._timestamps[idx])
        # Linearly interpolate
        interpolated_value = (1 - weight) * self._path[idx] + weight * self._path[idx + 1]
        return float(interpolated_value)
