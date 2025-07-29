import logging
from decimal import Decimal
from typing import Any, Literal, Optional, Tuple

import networkx as nx
import numpy as np
from numpy import linalg
from numpy.typing import NDArray

from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.spot.spot_array.deterministic_process_array import DeterministicSpotProcessArray
from nqs_sdk_extension.spot.spot_array.stochastic_process_array import StochasticSpotProcessArray
from nqs_sdk_extension.token_utils import wrap_token

from .data_provider.data_loader_factory import DataLoader


class SpotOracle:
    def __init__(
        self,
        stochastic_spot: StochasticSpotProcessArray,
        deterministic_spot: DeterministicSpotProcessArray,
        numeraire: str,
        current_timestamp: int,
        random_generator: Optional[RandomGenerator] = None,
        end_timestamp: Optional[int] = None,
        mandatory_tokens: Optional[list[str]] = None,
        execution_mode: Literal["simulation", "backtest"] = "simulation",
    ):
        super().__init__()
        if mandatory_tokens is None:
            mandatory_tokens = []
        self._validate(stochastic_spot, deterministic_spot, random_generator, end_timestamp)
        self.stochastic_spot = stochastic_spot
        self.deterministic_spot = deterministic_spot
        self.tokens = set(stochastic_spot.tokens).union(set(deterministic_spot.tokens))
        self.numeraire = wrap_token(numeraire)
        self.mandatory_tokens = [wrap_token(x) for x in mandatory_tokens]
        self.path_id: Optional[int] = None
        self.end_timestamp = end_timestamp
        self.spot_graph_is_connected = False
        self.current_timestamp = current_timestamp

        self.s0 = self.stochastic_spot.s0 | self.deterministic_spot.s0
        self.get_minimum_spanning_tree(execution_mode)
        self.connect_spot_graph()
        self.pairs = [process.pair for process in self.stochastic_spot.processes] + [
            process.pair for process in self.deterministic_spot.processes
        ]
        if self.stochastic_spot.need_calibration():
            self.stochastic_spot.calibrate_params(self.end_timestamp)  # type: ignore
            self.s0.update(self.stochastic_spot.s0)

        self._random_generator = random_generator
        self.std_normal_generator: Any = None
        self.token_decimals: dict[str, int] = {}

        self.U: NDArray[np.float64] = self.decompose_correlation_matrix()
        self.known_links: dict[Tuple[str, str], list[str]] = {}

    def set_seed(self, seed: int, use_antithetic_variates: bool) -> None:
        if self._random_generator is not None:
            self._random_generator.set_seed(seed, use_antithetic_variates)
            self.std_normal_generator = self._random_generator.process_dict["multidim_std_normal"].draw_single(
                dim=self.stochastic_spot.correlation.shape[0]
            )

    def set_token_decimals(self, decimals: dict[str, int]) -> None:
        self.token_decimals = decimals

    def set_timestamps_list(self, timestamps_list: list[int]) -> None:
        if len(self.deterministic_spot.processes) > 0:
            self.deterministic_spot.set_timestamps_list(timestamps_list)
            self.s0 = self.stochastic_spot.s0 | self.deterministic_spot.s0

    @staticmethod
    def _validate(
        stochastic_spot: StochasticSpotProcessArray,
        deterministic_spot: DeterministicSpotProcessArray,
        random_generator: RandomGenerator | None,
        end_timestamp: int | None,
    ) -> None:
        if (stochastic_spot.need_calibration() or deterministic_spot.has_historical_process()) and (
            not DataLoader.quantlib_source().is_source_configured() or end_timestamp is None
        ):
            raise ValueError(
                "data_loader, start date and end_timestamp must be provided if there are historical processes or if "
                "stochastic processes need calibration"
            )

        if len(stochastic_spot.processes) > 0 and random_generator is None:
            raise ValueError("Random generator must be provided if stochastic process are in the simulation")

        pairs = [process.pair for process in stochastic_spot.processes] + [
            process.pair for process in deterministic_spot.processes
        ]
        if len(set(pairs)) != len(pairs):
            raise ValueError("The processes list contains duplicates")

    def decompose_correlation_matrix(self) -> NDArray[np.float64]:
        try:
            u = (
                np.linalg.cholesky(self.stochastic_spot.correlation).T
                if self.stochastic_spot.correlation.shape[0] > 1
                else np.array([[1]])
            )
        except linalg.LinAlgError:
            raise ValueError("The spot correlation matrix is not positive-definite.")

        return np.array(u)

    def get_minimum_spanning_tree(self, execution_mode: Literal["simulation", "backtest"]) -> None:
        """
        Generate the minimum spanning tree from the list of spot pairs in order to simulate the minimum number of
        spots
        :return:
        """
        deterministic_edges = [spot.pair for spot in self.deterministic_spot.processes]
        stochastic_edges = [spot.pair for spot in self.stochastic_spot.processes]
        edgelist = deterministic_edges + stochastic_edges
        graph = nx.from_edgelist(edgelist)

        t = nx.minimum_spanning_tree(graph)
        self._spot_graph_is_connected = nx.is_connected(graph)
        # when we are in simulation mode, we remove the redundant spot pairs. In backtest mode, it is better to use
        # the historical spots requested in the parameters file, and avoid approximations that could come from
        # triangulations
        if len(t.edges) < len(graph.edges) and execution_mode == "simulation":
            redundant_spots = list(nx.difference(graph, t).edges())
            redundant_spots = [(i[0], i[1]) for i in redundant_spots]
            logging.warning(
                f"path_id:{self.path_id}: the set of processes is redundant. It is possible to simulate "
                f"the same pairs using a smaller set of spots. In particular {redundant_spots} can "
                f"and will not be directly simulated, as they can be obtained by triangulating other pairs"
            )
            for pair in redundant_spots:
                self.stochastic_spot.remove_process(pair)
                self.deterministic_spot.remove_process(pair)
                self.s0.pop(pair) if pair in self.s0.keys() else self.s0.pop((pair[1], pair[0]))

    def _evolve(self, block_timestamp: int) -> None:
        if self.stochastic_spot.processes:
            self.stochastic_spot.evolve(block_timestamp, next(self.std_normal_generator), self.U)
            self.current_timestamp = block_timestamp

    def update_all_spots(self, block_timestamp: int) -> None:
        if block_timestamp == self.current_timestamp:
            return
        elif block_timestamp < self.current_timestamp:
            raise ValueError(
                f"The spot oracle has been updated at block {self.current_timestamp} and it is being "
                f"queried at block {block_timestamp}"
            )
        else:
            self._evolve(block_timestamp)
            spots_value: dict = self.stochastic_spot.get_spot(block_timestamp)
            spots_value.update(self.deterministic_spot.get_spot(block_timestamp))
            self.s0 = spots_value
            self.current_timestamp = block_timestamp

    def get_selected_spots(self, pairs: list[Tuple[str, str]], block_timestamp: int) -> dict:
        self.update_all_spots(block_timestamp)
        spots = {}
        for pair in pairs:
            if pair[0] not in self.tokens or pair[1] not in self.tokens:
                raise ValueError(
                    f"Impossible to find the spot price for {pair}. Please make sure that both tokens "
                    f"are part of a simulated pair."
                )
            if pair in self.s0.keys():
                spots[pair] = self.s0[pair]
            else:
                spots[pair] = self.get_synthetic_spot(pair)
        return spots

    def get_path_links(self, pair: Tuple[str, str]) -> list[str]:
        if pair in self.known_links.keys():
            path = self.known_links[pair]
        else:
            edgelist = self.pairs
            graph = nx.from_edgelist(edgelist)
            path = nx.shortest_path(graph, source=pair[0], target=pair[1])
            self.known_links[pair] = path
        return path

    def get_synthetic_spot(self, pair: Tuple[str, str]) -> float:
        synthetic_spot = Decimal(1.0)
        path = self.get_path_links(pair)
        for i in range(len(path) - 1):
            spot_link = (path[i], path[i + 1])
            if spot_link in self.s0.keys():
                synthetic_spot *= Decimal(self.s0[spot_link])
            else:
                synthetic_spot /= Decimal(self.s0[(path[i + 1], path[i])])

        # use the same scaling that is adopted in the obsrevables to match what we get from the microlanguage
        # Expressions
        rounded_spot = round(synthetic_spot.scaleb(18))
        return float(Decimal(rounded_spot).scaleb(-18))

    def get_token_numeraire_spot(self, tokens: list[str], block_timestamp: int) -> dict[Tuple[str, str], float]:
        pairs = [(token, self.numeraire) for token in tokens]
        market_spot = self.get_selected_spots(pairs, block_timestamp=block_timestamp)
        return market_spot

    def connect_spot_graph(self) -> None:
        """
        If possible, generate extra spot pairs in order to connect all tokens in a graph
        :return:
        """
        # we generate missing link in the spot graph only if all processes are historical paths or
        # all processes are calibrated
        if (
            self._spot_graph_is_connected
            and self.numeraire in self.tokens
            and set(self.mandatory_tokens).issubset(self.tokens)
        ):
            return
        else:
            if not DataLoader.quantlib_source().is_source_configured():
                raise ValueError("Data Loader need to be valued in order to connect the spot graph")
            if len(self.stochastic_spot.processes) == 0:
                self.deterministic_spot.connect_spot_graph([self.numeraire] + self.mandatory_tokens)
            elif len(self.deterministic_spot.processes) == 0:
                self.stochastic_spot.connect_spot_graph([self.numeraire] + self.mandatory_tokens)
            else:
                raise ValueError(
                    "The spot pairs do not form a connected graph, please check again the list of"
                    "spot pairs. Missing pairs will be generated automatically if all processes are "
                    "calibrated or all processes are historical"
                )
            self.s0 = self.stochastic_spot.s0 | self.deterministic_spot.s0
