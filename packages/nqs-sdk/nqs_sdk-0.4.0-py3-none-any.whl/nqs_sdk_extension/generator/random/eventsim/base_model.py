from abc import ABC
from datetime import datetime
from typing import Optional

import numpy as np


class BaseModel(ABC):
    def __init__(
        self,
        support_seasonality: bool = False,
        weekly: bool = False,
        daily: bool = False,
        order: int = 3,
    ) -> None:
        self.supports_seasonality = support_seasonality
        self.set_seasonality(weekly, daily, order)

    @staticmethod
    def check_timestamp(timestamp: Optional[str]) -> None:
        if timestamp is None:
            raise ValueError("timestamp is required for simulation")

    def set_seasonality(self, weekly: bool = True, daily: bool = True, order: int = 3) -> None:
        if not self.supports_seasonality and (weekly or daily):
            raise ValueError(f"{type(self)} model does not support seasonality.")
        self.regressor: dict[str, float] = {}
        self.weekly = weekly
        if weekly:
            self.regressor.update({f"s(D={i}, period=W)": 0.0 for i in range(1, 8)})
        self.daily = daily
        self.order = order
        if daily:
            for i in range(1, order + 1):
                self.regressor[f"sin({i}, freq=D)"] = 0.0
                self.regressor[f"cos({i}, freq=D)"] = 0.0

    def get_seasonal_regressor(
        self,
        unix_timestamp: int,
    ) -> dict[str, float]:
        timestamp = datetime.utcfromtimestamp(unix_timestamp)
        weekday = timestamp.weekday() + 1
        timeofday = timestamp.hour + timestamp.minute / 60 + timestamp.second / 3600
        regressor = self.regressor.copy()
        if self.weekly:
            regressor[f"s(D={weekday}, period=W)"] = 1.0
        if self.daily:
            for i in range(1, self.order + 1):
                regressor[f"sin({i}, freq=D)"] = np.sin(2 * np.pi * i * timeofday / 24)
                regressor[f"cos({i}, freq=D)"] = np.cos(2 * np.pi * i * timeofday / 24)
        return regressor
