from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

import numpy as np

from nqs_sdk import BlockNumberOrTimestamp
from nqs_sdk_extension.spot.utils import get_wrapped_spot

from .data_provider.data_loader_factory import DataLoader


class SpotProcess(ABC):
    def __init__(self, pair: Tuple[str, str], current_timestamp: int):
        self.pair = get_wrapped_spot(pair)
        self.token0 = self.pair[0]
        self.token1 = self.pair[1]
        self.current_timestamp = current_timestamp
        self.s0 = -1.0
        self.token0_address: Optional[str] = None
        self.token1_address: Optional[str] = None
        self.pool_info: Optional[dict[Any, Any]] = None

    def get_token_address(self, token: str) -> str:
        """
        Retrieve the address of a given token
        :param token: the token symbol
        :return:
        """
        if token == self.token0 and self.token0_address:
            return self.token0_address
        if token == self.token1 and self.token1_address:
            return self.token1_address
        return DataLoader.quantlib_source().get_token_address("Ethereum", token)

    def set_token_address(self, token: str, token_address: str) -> None:
        """
        Sets the address of a token in the pair
        :param token: the token symbol
        :param token_address: the token address
        :return:
        """
        if token == self.token0:
            if not self.token0_address:
                self.token0_address = token_address
            elif self.token0_address != token_address:
                raise ValueError(
                    f"The stored address of {token} ({self.token0_address}), is trying to be"
                    f"overriden with {token_address}"
                )
            else:
                return
        elif token == self.token1:
            if not self.token1_address:
                self.token1_address = token_address
            elif self.token1_address != token_address:
                raise ValueError(
                    f"The stored address of {token} ({self.token1_address}), is trying to be"
                    f"overriden with {token_address}"
                )
            else:
                return
        else:
            raise ValueError(f"{token} is not in the list of tokens of spot {self.pair}")

    def set_pool_info(self, pool_info: dict) -> None:
        """
        Sets the attribute pools info
        :param pool_info: pool info
        :return:
        """
        if pool_info["spot"] == self.pair or pool_info["spot"] == (self.token1, self.token0):
            if not self.pool_info:
                self.pool_info = pool_info
        else:
            raise ValueError(f"Trying to set the attribute wrong pool_info attribute to the process {self.pair}")

    def get_historical_path(self, begin: int, limit: int, end: Optional[int] = None) -> tuple:
        """
        Returns the historical path of the pair
        :param timegrid:
        queried
        :return: the spot path
        """
        if self.pool_info is None:
            raise ValueError(
                f"Attempting to load historical spot values - Pool info not initialised for" f" the process {self.pair}"
            )

        begin_date = BlockNumberOrTimestamp.timestamp(begin)
        end_date = BlockNumberOrTimestamp.timestamp(end) if end is not None else None

        close_timestamps, close_prices = DataLoader.quantlib_source().get_spot_values(
            self.pool_info["pool_address"], begin_date, end_date, limit
        )

        if self.pool_info["spot"] != self.pair:
            close_prices = np.array(close_prices, dtype=np.float64)
            close_prices = 1.0 / close_prices
        if np.isnan(close_prices).any():
            raise ValueError(
                f" Missing historical prices for {self.pair}, between timestamps "
                f"{str(close_timestamps[0])} and {str(close_timestamps[-1])}"
            )

        # close_prices = close_prices.reshape((len(close_prices), 1))
        close_prices = np.array(close_prices).reshape((len(close_prices), 1))

        close_timestamps = np.array(close_timestamps)
        return close_prices, close_timestamps

    def get_historical_path_at_timestamps(self, timegrid: list[int]) -> Any:
        """
        Returns the historical path of the pair
        :param timegrid:
        queried
        :return: the spot path
        """
        if self.pool_info is None:
            raise ValueError(
                f"Attempting to load historical spot values - Pool info not initialised for" f" the process {self.pair}"
            )
        close_prices = DataLoader.quantlib_source().get_spot_values_at_timestamps(
            self.pool_info["pool_address"], timegrid
        )
        if len(close_prices) != len(timegrid):
            raise ValueError(
                f"Discrepancies between the number of requested prices and "
                f"the number of returned prices for pair {self.pair}, pool address "
                f"{self.pool_info['pool_address']}"
            )
        if self.pool_info["spot"] != self.pair:
            close_prices = 1 / close_prices
        if np.isnan(close_prices).any():
            raise ValueError(
                f" Missing historical prices for {self.pair}, between timestamps "
                f"{str(timegrid[0])} and {str(timegrid[-1])}"
            )

        spot_path = np.array(close_prices).reshape((len(close_prices), 1))
        return spot_path

    @abstractmethod
    def get_spot(self, timestamp: int) -> float:
        pass
