import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np
from nqs_pycore import Wallet

from nqs_sdk_extension.agent.agent_action import CustomVariable
from nqs_sdk_extension.observer.utils import is_valid_metric_name
from nqs_sdk_extension.spot.spot_oracle import SpotOracle

SPOT_OBSERVER_ID = "spot_observer"
DEFAULT_DECIMALS = 18


@dataclass
class SingleObservable(ABC):
    """
    The value of an observable at a timestamp
    """

    value: int
    decimals: int | float  # the decimals of Uniswap liquidity in corner cases can be float


@dataclass
class ObservablesTS(ABC):
    """
    Timestamps, values and number of decimals for the Observables timeseries
    """

    decimals: int | float
    block_timestamps: list[int] = field(default_factory=list)
    values: list[int] = field(default_factory=list)


class ABCObserver(ABC):
    def __init__(self) -> None:
        self._observables: dict[str, ObservablesTS] = {}
        self._observer_id: str = ""
        self.spot_oracle: SpotOracle

    # ------------------- Abstract methods -------------------

    @abstractmethod
    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, "ABCObserver"]]) -> None:
        """
        Method to set variables coming from the environment
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        pass

    def collect_observables(self, block_number: int, block_timestamp: int) -> None:
        new_observables = self.get_all_observables(block_number, block_timestamp)
        # save observables
        self._append_new_observables(block_number, block_timestamp, new_observables)

    @abstractmethod
    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        pass

    @abstractmethod
    def get_custom_variable(self, variable_name: str) -> "CustomVariable":
        pass

    def flush_buffer(self) -> None:
        pass

    # ------------------- Public methods -------------------
    def set_oracle(self, spot_oracle: Optional[SpotOracle]) -> None:
        if spot_oracle is None:
            raise ValueError("The spot oracle must be set in every observer")
        self.spot_oracle = spot_oracle
        self.numeraire_decimals = self.spot_oracle.token_decimals[self.spot_oracle.numeraire]

    def get_metric_value_timeseries(
        self, metric_name: str, block_number: int, block_timestamp: int
    ) -> Tuple[np.ndarray, np.ndarray, int | float]:
        if metric_name in self._observables:
            values, timeseries, decimals = (
                self._observables[metric_name].values,
                self._observables[metric_name].block_timestamps,
                self._observables[metric_name].decimals,
            )
        else:
            # XXX temporary patch for backward compatibility
            _, metric_name = metric_name.split(".", maxsplit=1)
            if metric_name in self._observables:
                values, timeseries, decimals = (
                    self._observables[metric_name].values,
                    self._observables[metric_name].block_timestamps,
                    self._observables[metric_name].decimals,
                )
            else:
                # if the timeseries have not been created, return an empty array
                values, timeseries, decimals = [], [], 0

        return np.array(values, dtype=np.object_), np.array(timeseries, dtype=np.uint32), int(decimals)

    def get_all_metrics(self) -> dict[str, dict[str, list]]:
        # metrics are passed as float (human-readable) numbers
        # XXX temporary patch for backward compatibility
        observables: dict[str, dict[str, list]] = {}
        for key, timeseries in self._observables.items():
            if not is_valid_metric_name(key):
                key = self._observer_id + "." + key
            observables[key] = {}
            observables[key]["block_timestamps"] = timeseries.block_timestamps
            observables[key]["values"] = [x / 10**timeseries.decimals for x in timeseries.values]
        return observables

    # ------------------- Protected methods -------------------

    def _append_new_observables(
        self, block_number: int, block_timestamp: int, new_observables: dict[str, SingleObservable]
    ) -> None:
        logging.debug(f"Appending new observables at block {block_number}")
        logging.debug(f"New observables: {new_observables}")
        for key, observable in new_observables.items():
            self._observables.setdefault(key, ObservablesTS(decimals=observable.decimals))
            self._observables[key].block_timestamps.append(block_timestamp)
            self._observables[key].values.append(observable.value)
