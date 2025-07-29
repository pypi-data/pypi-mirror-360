from abc import ABC, abstractmethod
from typing import Any, Sequence, Tuple

import networkx as nx

from nqs_sdk_extension.spot.spot_process import SpotProcess


class SpotProcessArray(ABC):
    def __init__(self, processes: Sequence[SpotProcess]):
        self.processes = processes
        self.current_timestamp = processes[0].current_timestamp if processes else -1
        self.tokens = self.get_tokens_list()
        self.s0 = {process.pair: process.s0 for process in self.processes}
        self._validate_current_timestamp()

    def _validate_current_timestamp(self) -> None:
        if len(self.processes) == 0:
            return
        current_timestamps = [process.current_timestamp for process in self.processes]
        if len(set(current_timestamps)) != 1:
            raise ValueError("All processes need to start from the same timestamp")

    @abstractmethod
    def _add_spot_graph_link(self, condition: bool, token: str) -> str:
        """
        Adds an underlying process to the spot graph
        :param condition: a boolean condition used to check if WETH or USDT will be used as a connecting link
        :param token: the token to add to the spot graph
        :return: the extra token (WETH or USDT), that paired with the input token forms the added underlying spot
        """
        pass

    @abstractmethod
    def _is_linkable(self) -> bool:
        """
        Returns if is possible to create missing links in the spot graph
        :return:
        """
        pass

    def connect_spot_graph(self, tokens: list[str]) -> None:
        """
        If possible, connects the spot graph by adding missing links
        :param tokens: the tokens to be added to the spot graph, usually the numeraire and USDC
        :return:
        """
        edgelist = [(process.pair[0], process.pair[1]) for process in self.processes]
        graph = nx.from_edgelist(edgelist)
        weth_in_graph = "WETH" in self.tokens

        for token in tokens:
            if token not in self.tokens:
                if not (self._is_linkable()):
                    raise ValueError(
                        "It is impossible to create new spot pairs. To do so all pairs need to be either historical "
                        "processes or calibrated stochastic processes"
                    )
                extra_token = self._add_spot_graph_link(token != "WETH", token)
                self.s0[(token, extra_token)] = self.processes[-1].s0
                graph.add_edge(token, extra_token)

            if not nx.is_connected(graph):
                if not (self._is_linkable()):
                    raise ValueError(
                        "It is impossible to create new spot pairs. To do so all pairs need to be either historical "
                        "processes or calibrated stochastic processes"
                    )
                for subgraph in nx.connected_components(graph):
                    selected_token = list(subgraph)[0]
                    extra_token = self._add_spot_graph_link(
                        (weth_in_graph and "WETH" not in subgraph) or not weth_in_graph, selected_token
                    )
                    graph.add_edge(selected_token, extra_token)

                    if nx.is_connected(graph):
                        break

    def get_tokens_list(self) -> set[str]:
        """
        Returns the list of tokens in the multispot process
        :return: the list of token symbols
        """
        tokens = []
        for process in self.processes:
            tkns = list(process.pair)
            tokens.extend(tkns)
        return set(tokens)

    def get_spot(self, timestamp: int) -> dict[tuple[str, str], float]:
        return {process.pair: process.get_spot(timestamp) for process in self.processes}

    @abstractmethod
    def get_tokens_address(self) -> dict[str, str]:
        """
        Return the dictionary of token addresses
        :return: the dictionary containing all token addresses
        """
        pass

    @abstractmethod
    def get_pools_info(self) -> dict[Tuple[str, str], Any]:
        """
        Returns the pool info for all the underlying processes
        :return: a dictionary that associates to each underlying pair the dictionary of pool info
        """
        pass

    @abstractmethod
    def remove_process(self, pair: Tuple[str, str]) -> None:
        """
        Remove a process from the list
        :param pair: the spot pair to be removed
        :return:
        """
        pass
