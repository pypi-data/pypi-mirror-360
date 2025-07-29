import bisect
from datetime import datetime
from typing import Any, Literal, Optional, Tuple

from sortedcontainers import SortedDict

from nqs_sdk_extension.constants import SPOT_BATCH_SIZE
from nqs_sdk_extension.spot.spot_process import SpotProcess

from ..data_provider.data_loader_factory import DataLoader


class HistoricalProcess(SpotProcess):
    def __init__(self, pair: Tuple[str, str], **kwargs: Any):
        super().__init__(pair, kwargs["current_timestamp"])
        self.execution_mode: Literal["simulation", "backtest"] = kwargs["execution_mode"]
        self.simulation_end_timestamp = kwargs["end_timestamp"]
        self.process_start_timestamp = self.get_initial_timestamp(kwargs.get("process_start_timestamp"))
        self.process_end_timestamp: int = self.process_start_timestamp + (
            kwargs["end_timestamp"] - kwargs["current_timestamp"]
        )
        self.token0_address = self.get_token_address(self.token0)
        self.token1_address = self.get_token_address(self.token1)
        self.pool_info = DataLoader.quantlib_source().get_pool_info(
            self.token0, self.token1, self.token0_address, self.token1_address
        )

        self._validate()

        self.timestamps_list: list[int] = (
            self.generate_timestamps_list() if self.process_start_timestamp != self.current_timestamp else []
        )
        self.path: SortedDict[int, float] = (
            self.initialise_path() if self.process_start_timestamp != self.current_timestamp else {}
        )
        _, self.s0 = self.path.peekitem(0) if self.process_start_timestamp != self.current_timestamp else (0, -1)

    def initialise_path(self) -> SortedDict[int, float]:
        # in simulation mode it is not possible to query additional data during the simulation - hence all the spot
        # path has to be loaded at the beginning of the simulation
        if self.execution_mode == "backtest":
            close_prices, close_timestamps = self.get_historical_path(
                begin=self.timestamps_list[0], end=self.timestamps_list[-1], limit=SPOT_BATCH_SIZE
            )  # arbitrary first fetch
            return SortedDict(
                zip(
                    close_timestamps.flatten(),
                    close_prices.flatten(),
                )
            )
        else:
            path: SortedDict[int, float] = SortedDict()
            start_time = self.timestamps_list[0]
            while start_time < self.timestamps_list[-1]:
                close_prices, close_timestamps = self.get_historical_path(
                    begin=start_time, end=self.timestamps_list[-1], limit=SPOT_BATCH_SIZE
                )
                path.update(
                    SortedDict(
                        zip(
                            close_timestamps.flatten(),
                            close_prices.flatten(),
                        )
                    )
                )
                if len(close_timestamps) < SPOT_BATCH_SIZE:
                    break
                start_time = close_timestamps[-1] + 1
            return path

    def set_timestamps_list(self, timestamps: list[int]) -> None:
        if not self.timestamps_list:
            self.timestamps_list = timestamps
            self.path = self.initialise_path()
            _, self.s0 = self.path.peekitem(0)

    def get_initial_timestamp(self, process_initial_timestamp: Optional[int]) -> int:
        if process_initial_timestamp is None:
            return self.current_timestamp
        else:
            return process_initial_timestamp

    def _validate(self) -> None:
        if datetime.utcfromtimestamp(self.process_end_timestamp) > datetime.now():
            raise ValueError(f"The historical process {self.pair} end timestamp is past today.")

    def generate_timestamps_list(self) -> list[int]:
        return DataLoader.quantlib_source().get_timestamps_from_interval(
            self.process_start_timestamp, self.process_end_timestamp
        )

    def get_spot(self, timestamp: int) -> float:
        """
        Returns the historical spot value
        :param timestamp: the timestamp at which the spot must be queried
        :return:
        """
        process_timestamp = self.process_start_timestamp + timestamp - self.current_timestamp

        if process_timestamp > list(self.path.keys())[-1] and self.execution_mode == "backtest":
            # fetch next timestamps
            close_prices, close_timestamps = self.get_historical_path(
                begin=process_timestamp, limit=SPOT_BATCH_SIZE, end=self.process_end_timestamp
            )
            self.path = SortedDict(zip(close_timestamps.flatten(), close_prices.flatten()))
            _, self.s0 = self.path.peekitem(0)

        # return the spot right before the last known value
        index = bisect.bisect_right(list(self.path.keys()), process_timestamp)
        return float(self.path[list(self.path.keys())[index - 1]])
