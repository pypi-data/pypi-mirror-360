from datetime import datetime
from typing import Any, List, Tuple

import numpy as np
from numpy.typing import NDArray

from nqs_sdk_extension.spot.spot_array.spot_process_array import SpotProcessArray
from nqs_sdk_extension.spot.stochastic_process.gbm_process import GBMProcess
from nqs_sdk_extension.spot.stochastic_process.stochastic_process import StochasticProcess
from nqs_sdk_extension.spot.stochastic_process.wgn_process import WGNProcess
from nqs_sdk_extension.spot.utils import datetime64_to_timestamp, timestamp_to_string
from nqs_sdk_extension.token_utils import ETH_STABLE_PAIRS, STABLECOINS

from ..data_provider.data_loader_factory import DataLoader


class StochasticSpotProcessArray(SpotProcessArray):
    def __init__(self, processes: List[StochasticProcess], correlation: NDArray[np.float64]):
        super().__init__(processes)
        self.processes: List[StochasticProcess] = processes
        self.processes_to_calibrate = [process for process in processes if process.calibrate]
        self.correlation = (
            np.eye(len(self.processes))
            if len(self.processes) == len(self.processes_to_calibrate)
            else np.array(correlation)
        )
        self._validate_data_loader()
        self.tokens_address: dict[str, str] = self.get_tokens_address()
        self.pools_info: dict[Tuple[str, str], dict[str, Any]] = self.get_pools_info()

    def _validate_data_loader(self) -> None:
        if self.processes:
            if self.need_calibration() and not DataLoader.quantlib_source().is_source_configured():
                raise ValueError(
                    "The StochasticSpotProcessArray needs to be initialised with a data_loader when "
                    "there are processes to calibrate"
                )
            if len(self.processes) > 1:
                if len(self.processes) != self.correlation.shape[0] or len(self.processes) != self.correlation.shape[1]:
                    raise ValueError(
                        "Correlation has to be a square matrix with as many rows as there are "
                        "stochastic processes to simulate"
                    )

    def _is_linkable(self) -> bool:
        """
        Returns if the all processes are calibrated
        :return:
        """
        return len(self.processes) == len(self.processes_to_calibrate)

    def add_process(self, process: StochasticProcess) -> None:
        """
        Add a process to the list of underlying processes
        :param process: the process to add
        :return:
        """
        for proc in self.processes:
            if proc.pair == process.pair or proc.pair == (process.pair[1], process.pair[0]):
                raise ValueError(
                    f"Trying to add {proc.pair} to the list of processes, but there is already a process"
                    f"for that pair"
                )
        n_processes = len(self.processes)
        self.processes += [process]

        new_correlation = np.zeros((n_processes + 1, n_processes + 1))
        new_correlation[:n_processes, :n_processes] = self.correlation
        new_correlation[n_processes, n_processes] = 1
        self.correlation = new_correlation

        if process.calibrate:
            if not DataLoader.quantlib_source().is_source_configured():
                raise ValueError(
                    f"Impossible to add the calibrated pair {process.pair} as the data_loader is not provided"
                )
            self.processes_to_calibrate += [process]
            for token in [process.token0, process.token1]:
                if token in self.tokens:
                    process.set_token_address(token, self.tokens_address[token])
                else:
                    address = process.get_token_address(token)
                    process.set_token_address(token, address)
                    self.tokens_address[token] = address
            pool_info = DataLoader.quantlib_source().get_pool_info(
                process.token0,
                process.token1,
                process.token0_address,  # type: ignore
                process.token1_address,  # type: ignore
            )
            self.pools_info[process.pair] = pool_info
            process.set_pool_info(pool_info)

        self.tokens.update([process.token0, process.token1])
        self.s0[process.pair] = process.s0

    def remove_process(self, pair: Tuple[str, str]) -> None:
        """
        Remove a process from the list
        :param pair: the spot pair to be removed
        :return:
        """
        inverse_pair = (pair[1], pair[0])
        process_to_remove = [
            process for process in self.processes if process.pair == pair or process.pair == inverse_pair
        ]

        if len(process_to_remove) == 0:
            return

        process_index = self.processes.index(process_to_remove[0])
        self.processes.remove(process_to_remove[0])
        self.processes_to_calibrate = [process for process in self.processes if process.calibrate]
        self.tokens = self.get_tokens_list()
        self.s0.pop(process_to_remove[0].pair)
        self.correlation = np.delete(self.correlation, process_index, axis=0)
        self.correlation = np.delete(self.correlation, process_index, axis=1)

    def set_correlation(self, new_correlation: NDArray[np.float64]) -> None:
        """
        Sets the correlation matrix
        :param new_correlation: the new correlation
        :return:
        """
        self.correlation = new_correlation

    def get_tokens_address(self) -> dict[str, str]:
        """
        Return the dictionary of token addresses
        :return: the dictionary containing all token addresses
        """
        tokens_address: dict[str, str] = {}
        for process in self.processes_to_calibrate:
            for token in [process.token0, process.token1]:
                if token in tokens_address.keys():
                    process.set_token_address(token, tokens_address[token])
                else:
                    address = process.get_token_address(token)
                    process.set_token_address(token, address)
                    tokens_address[token] = address
        return tokens_address

    def get_pools_info(self) -> dict[Tuple[str, str], dict[str, Any]]:
        """
        Returns the pool info for all the underlying processes
        :return: a dictionary that associates to each underlying pair the dictionary of pool info
        """
        pools_info = {}
        for process in self.processes_to_calibrate:
            pool_info = DataLoader.quantlib_source().get_pool_info(
                process.token0,
                process.token1,
                process.token0_address,  # type: ignore
                process.token1_address,  # type: ignore
            )
            pools_info[process.pair] = pool_info
            process.set_pool_info(pool_info)
        return pools_info

    def need_calibration(self) -> bool:
        """
        Returns if there are underlying processes to calibrate
        :return:
        """
        return len(self.processes_to_calibrate) > 0

    @staticmethod
    def generate_calibration_timegrid(end_time: float) -> Tuple[list[float], list[float]]:
        """
        Generate the timegrid used for calibration
        :param end_time: the end time of the simulation
        :return:
        """
        times = list(np.linspace(0, end_time, int(365 * end_time)))
        if len(times) < 10:
            new_times = [x for x in np.linspace(0, end_time, 10) if x not in times]
            times_enriched = new_times + times
            times_enriched.sort()
        else:
            times_enriched = times
        return times, times_enriched

    def calibrate_correlation_matrix(self, spot_path: NDArray[np.float64]) -> None:
        """
        Calibrate the correlation matrix
        :param spot_path: the historical spot path used to calibrate the correlation
        :return:
        """
        correl_matrix = np.corrcoef(spot_path)
        if np.any(np.isnan(correl_matrix)):
            raise ValueError(
                "Impossible to compute correlation matrix, please check the consistency of data for spots processes"
            )

        calibrated_spot_indices = [
            i for i in range(len(self.processes)) if self.processes[i] in self.processes_to_calibrate
        ]
        self.correlation[np.ix_(calibrated_spot_indices, calibrated_spot_indices)] = correl_matrix

    def calibrate_params(self, end_timestamp: int) -> None:
        """
        Calibrate the underlying spot processes and the correlation matrix
        :param end_timestamp: the end timestamp of the simulation
        :return:
        """
        start_date = datetime.utcfromtimestamp(self.current_timestamp)
        end_date = datetime.utcfromtimestamp(end_timestamp)
        delta_days = (end_date - start_date).days
        dt = delta_days / 365 if delta_days > 0 else 1 / 365
        _, times_enriched = self.generate_calibration_timegrid(dt)
        spot_paths_enriched = []

        start_date_py = np.datetime64(timestamp_to_string(self.current_timestamp))
        end_date_py_arr = [start_date_py + np.timedelta64(int(x * 365 * 24 * 3600), "s") for x in times_enriched]
        # correct for timezone
        timegrid = [datetime64_to_timestamp(x) for x in end_date_py_arr]

        for process in self.processes_to_calibrate:
            spot_paths_enriched.append(process.get_historical_path_at_timestamps(timegrid))

        spot_paths_enriched_reshaped = np.array([x.reshape(len(times_enriched)) for x in spot_paths_enriched])

        for i, process in enumerate(self.processes_to_calibrate):
            process.calibrate_params(spot_paths_enriched_reshaped[i])
            self.s0[process.pair] = process.s0

        if len(self.processes_to_calibrate) > 1:
            self.calibrate_correlation_matrix(spot_paths_enriched_reshaped)

    def _add_spot_graph_link(self, condition: bool, token: str) -> str:
        """
        Adds an underlying process to the spot graph
        :param condition: a boolean condition used to check if WETH or USDT will be used as a connecting link
        :param token: the token to add to the spot graph
        :return: the extra token (WETH or USDT), that paired with the input token forms the added underlying spot
        """
        extra_token = "WETH" if condition else "USDT"
        is_stable_pair = (token in ETH_STABLE_PAIRS) if condition else (token in STABLECOINS)

        process_class = WGNProcess if is_stable_pair else GBMProcess
        self.add_process(
            process_class(pair=(token, extra_token), s0=1.0, calibrate=True, current_timestamp=self.current_timestamp)
        )
        self.s0[(token, extra_token)] = self.processes[-1].s0
        # set this only to have the right shape, as it will not be used
        self.correlation = np.eye(len(self.processes))
        return extra_token

    def evolve(self, next_timestamp: int, dz: np.ndarray, u: np.ndarray) -> None:
        """
        Evolves all the underlying spot processes
        :param dz: the brownian motion increment
        :param u: choleski decomposition of the correlation matrix
        :param next_timestamp: the timestamp after the evolve action has been executed
        :return:
        """
        start_date = datetime.utcfromtimestamp(self.current_timestamp)
        end_date = datetime.utcfromtimestamp(next_timestamp)
        dt = (end_date - start_date).total_seconds() / (3600 * 24 * 365)
        dw = dz @ u
        if dt <= 0:
            raise ValueError(
                f"Trying to evolve stochastic processes from timestamp {self.current_timestamp} to time "
                f"{next_timestamp}, "
                f"but {next_timestamp} <= {self.current_timestamp}"
            )
        for i, process in enumerate(self.processes):
            process.evolve(dt, dw[0][i], next_timestamp)
        self.current_timestamp = next_timestamp
        self.s0 = {process.pair: process.s0 for process in self.processes}
