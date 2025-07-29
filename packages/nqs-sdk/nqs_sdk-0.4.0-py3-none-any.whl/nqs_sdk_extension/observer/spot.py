from dataclasses import asdict
from decimal import Decimal
from typing import Dict, Optional, Tuple

import numpy as np
from nqs_pycore import Wallet
from numpy.typing import NDArray

from nqs_sdk_extension.agent.agent_action import CustomVariable
from nqs_sdk_extension.observer.abc_observer import DEFAULT_DECIMALS, ABCObserver, SingleObservable
from nqs_sdk_extension.observer.utils import make_metric_name, parse_metric_name
from nqs_sdk_extension.wallet import rescale_to_int


class SpotObserver(ABCObserver):
    def __init__(self) -> None:
        super().__init__()
        self.metric_names: dict[tuple[str, str], str] = {}

    def create_metric_names(self) -> None:
        for pair in self.spot_oracle.s0.keys():
            self.metric_names[pair] = make_metric_name("common", "market_spot", pair=f"{pair[0]}/{pair[1]}")

    def get_selected_spot_ts(
        self,
        pair: Tuple[str, str],
        block_timestamp: int,
    ) -> Tuple[NDArray, NDArray, int | float]:
        self.spot_oracle.update_all_spots(block_timestamp)
        if pair[0] not in self.spot_oracle.tokens or pair[1] not in self.spot_oracle.tokens:
            raise ValueError(
                f"Impossible to find the spot price for {pair}. Please make sure that both tokens "
                f"are part of a simulated pair."
            )
        if pair in self.spot_oracle.s0.keys():
            synthetic_spot = asdict(
                self._observables[make_metric_name("common", "market_spot", pair=f"{pair[0]}/{pair[1]}")]
            )
            return (
                np.array(synthetic_spot["values"], dtype=np.object_),
                np.array(synthetic_spot["block_timestamps"], dtype=np.uint32),
                DEFAULT_DECIMALS,
            )

        else:
            synthetic_spot = {}
            path = self.spot_oracle.get_path_links(pair)
            for i in range(len(path) - 1):
                spot_link = (path[i], path[i + 1])
                if (path[i], path[i + 1]) in self.spot_oracle.s0.keys():
                    if len(synthetic_spot) > 0:
                        synthetic_spot["values"] = [
                            Decimal(synthetic_spot["values"][j])
                            * Decimal(self._observables[self.metric_names[spot_link]].values[j]).scaleb(
                                -DEFAULT_DECIMALS
                            )
                            for j in range(len(synthetic_spot["values"]))
                        ]
                    else:
                        synthetic_spot = asdict(self._observables[self.metric_names[spot_link]])
                else:
                    if len(synthetic_spot) > 0:
                        synthetic_spot["values"] = [
                            Decimal(synthetic_spot["values"][j]).scaleb(DEFAULT_DECIMALS)
                            / Decimal(self._observables[self.metric_names[(path[i + 1], path[i])]].values[j])
                            for j in range(len(synthetic_spot["values"]))
                        ]
                    else:
                        synthetic_spot = asdict(self._observables[self.metric_names[(path[i + 1], path[i])]])
                        synthetic_spot["values"] = [
                            Decimal(1).scaleb(DEFAULT_DECIMALS) / Decimal(x).scaleb(-DEFAULT_DECIMALS)
                            for x in synthetic_spot["values"]
                        ]
            return (
                np.array([round(x) for x in synthetic_spot["values"]], dtype=np.object_),
                np.array(synthetic_spot["block_timestamps"], dtype=np.uint32),
                DEFAULT_DECIMALS,
            )

    def get_metric_value_timeseries(
        self, metric_name: str, block_number: int, block_timestamp: int
    ) -> Tuple[np.ndarray, np.ndarray, int | float]:
        metric_name_dict = parse_metric_name(metric_name)
        if metric_name_dict["metric"] != "market_spot":
            raise ValueError("Only 'market_spot' metric is supported for 'common' protocol")
        return self.get_selected_spot_ts(tuple(metric_name_dict["pair"].split("/")), block_timestamp)

    def set_environment(self, observable_id: str, env_observers: Optional[Dict[str, ABCObserver]]) -> None:
        self._observer_id = observable_id
        self.create_metric_names()

    def get_all_observables(self, block_number: int, block_timestamp: int) -> dict[str, SingleObservable]:
        self.spot_oracle.update_all_spots(block_timestamp)
        new_observables = {
            self.metric_names[pair]: SingleObservable(rescale_to_int(spot, DEFAULT_DECIMALS), DEFAULT_DECIMALS)
            for pair, spot in self.spot_oracle.s0.items()
        }
        return new_observables

    ######### agent specific    ##############################################################################
    def get_agent_observables(
        self, block_number: int, block_timestamp: int, wallet: Wallet
    ) -> dict[str, SingleObservable]:
        return {}

    def get_custom_variable(self, variable_name: str) -> CustomVariable:
        raise NotImplementedError
