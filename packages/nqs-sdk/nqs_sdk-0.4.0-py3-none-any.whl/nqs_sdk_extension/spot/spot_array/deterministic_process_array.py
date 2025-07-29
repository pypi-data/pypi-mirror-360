import functools
import logging
import operator
from typing import Any, List, Literal, Optional, Tuple, Union

from nqs_sdk_extension.spot.deterministic_process.custom_process import CustomProcess
from nqs_sdk_extension.spot.deterministic_process.historical_process import HistoricalProcess
from nqs_sdk_extension.spot.spot_array.spot_process_array import SpotProcessArray
from nqs_sdk_extension.spot.spot_process import SpotProcess


class DeterministicSpotProcessArray(SpotProcessArray):
    def __init__(
        self,
        processes: List[Union[HistoricalProcess, CustomProcess]],
        execution_mode: Optional[Literal["backtest", "simulation"]] = None,
    ):
        super().__init__(processes)
        self.processes = processes
        self.simulation_end_timestamp = self.processes[0].simulation_end_timestamp if self.processes else -1
        self.execution_mode = execution_mode

    def remove_process(self, pair: Tuple[str, str]) -> None:
        """
        Remove a process from the list
        :param pair: the spot pair to be removed
        :return:
        """
        inverse_pair = (pair[1], pair[0])
        self.processes = [process for process in self.processes if process.pair not in [pair, inverse_pair]]

    def _is_linkable(self) -> bool:
        """
        Returns whether all the underlying processes are historical
        :return:
        """
        return all(bool(process.pool_info) for process in self.processes)

    def has_historical_process(self) -> bool:
        """
        Returns whether any of the underlying processes are historical
        :return:
        """
        return any(bool(process.pool_info) for process in self.processes)

    def get_tokens_address(self) -> dict[str, str]:
        """
        Return the dictionary of token addresses
        :return: the dictionary containing all token addresses
        """
        token_addresses = {}
        for process in self.processes:
            if process.token0_address is not None:
                token_addresses[process.token0] = process.token0_address
            if process.token1_address is not None:
                token_addresses[process.token1] = process.token1_address
        return token_addresses

    def get_pools_info(self) -> dict[Tuple[str, str], Any]:
        """
        Returns the pool info for all the underlying processes
        :return: a dictionary that associates to each underlying pair the dictionary of pool info
        """
        pools_info = {}
        for process in self.processes:
            if process.pool_info is not None:
                pools_info[process.pair] = process.pool_info
        return pools_info

    def _add_spot_graph_link(self, condition: bool, token: str) -> str:
        """
        Adds an underlying process to the spot graph
        :param condition: a boolean condition used to check if WETH or USDT will be used as a connecting link
        :param token: the token to add to the spot graph
        :param start_timestamp: the starting timestamp of the simulation
        :return: the extra token (WETH or USDT), that paired with the input token forms the added underlying spot
        """
        extra_token = "WETH" if condition else "USDT"
        logging.info(
            f"Adding the Historical Process {(token, extra_token)}, with starting timestamp {self.current_timestamp}"
        )
        self.add_process(
            HistoricalProcess(
                pair=(token, extra_token),
                current_timestamp=self.current_timestamp,
                process_start_timestamp=self.current_timestamp,
                end_timestamp=self.simulation_end_timestamp,
                execution_mode=self.execution_mode,
            )
        )
        self.s0[(token, extra_token)] = self.processes[-1].s0
        return extra_token

    def add_process(self, process: SpotProcess) -> None:
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
        self.processes = functools.reduce(operator.add, [self.processes, [process]])
        self.tokens.update([process.token0, process.token1])
        self.s0[process.pair] = process.s0

    def set_timestamps_list(self, timestamps: list[int]) -> None:
        for process in self.processes:
            if isinstance(process, HistoricalProcess):
                process.set_timestamps_list(timestamps)
                self.s0[process.pair] = process.s0
