import copy
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nqs_sdk_extension.constants import BENCHMARK_AGENT_NAME
from nqs_sdk_extension.token_utils import wrap_token


class BenchmarkStrategyName(Enum):
    LONG_TOKEN = "long_token"
    HODL = "hodl"


@dataclass
class BenchmarkStrategy:
    benchmark_strategy_name: BenchmarkStrategyName = field(init=False)

    @abstractmethod
    def create_benchmark_agent(self, benchmark_agent: dict, **kwargs: Any) -> None:
        """
        @notice update the dict benchmark_agent with timed or continuous events.
        @param benchmark_agent the raw benchmark agent config, with a wallet but no strategy
        @param **kwargs some more arguments for the specific benchmark strategy
        """
        pass

    @property
    @abstractmethod
    def tokens_used_in_benchmark(self) -> set[str]:
        """
        @notice returns the set of tokens used in the benchmark strategy
        """
        pass


# Define the sub-objects
@dataclass
class LongToken(BenchmarkStrategy):
    token_to_long: str

    def __post_init__(self) -> None:
        self.benchmark_strategy_name = BenchmarkStrategyName.LONG_TOKEN
        self.token_to_long = wrap_token(self.token_to_long)

    def create_benchmark_agent(self, benchmark_agent: dict, **kwargs: Any) -> None:
        benchmark_agent_name = kwargs["benchmark_agent_name"]
        block_number_start = kwargs["block_number_start"]

        # swap all tokens to the token_to_long using the cex at initial time
        list_of_actions = [
            {
                "action_name": "swap",
                "condition": None,
                "protocol_id": "cex",
                "name": "swap",
                "args": {
                    "token_to_sell": token,
                    "token_to_buy": self.token_to_long,
                    "amount_to_sell": f'{benchmark_agent_name}.all.wallet_holdings:{{token="{token}"}}',
                },
            }
            for token in benchmark_agent["wallet"].keys()
        ]
        benchmark_agent["strategy"]["timed_events"].append(
            {"name": "swap-all-to-token", "block_number": block_number_start, "actions": list_of_actions}
        )

    @property
    def tokens_used_in_benchmark(self) -> set[str]:
        return {self.token_to_long}


@dataclass
class Hodl(BenchmarkStrategy):
    def __post_init__(self) -> None:
        self.benchmark_strategy_name = BenchmarkStrategyName.HODL

    def create_benchmark_agent(self, benchmark_agent: dict, **kwargs: Any) -> None:
        pass

    @property
    def tokens_used_in_benchmark(self) -> set[str]:
        return set()


class Benchmark:
    def __init__(self, agent_name: str, benchmark_config: dict, benchmark_id: int):
        self.strategy: BenchmarkStrategy
        self.agent_name = agent_name
        self.benchmark_id = benchmark_id
        self._create_from_config(benchmark_config)

    def _create_from_config(self, config: dict) -> None:
        self._set_strategy(config)

    def _set_strategy(self, config: dict) -> None:
        strategy_name: str = config["strategy_name"]
        if strategy_name == "long_token":
            self.strategy = LongToken(token_to_long=config["params"]["token"])
        elif strategy_name == "hodl":
            self.strategy = Hodl()
        else:
            raise ValueError(f"Invalid benchmark strategy name: {strategy_name}...")

    def add_benchmark_agent(self, global_parameters: dict, agent_wallet: dict, block_number_start: int) -> None:
        """
        @notice creates and adds the benchmark agent to the global parameters
        @param global_parameters the global parameters of the simulation, defined in the config file
        @param agent_wallet the initial wallet of the agent to create the benchmark against
        @param block_number_start the first block of the simulation
        """
        benchmark_agent_name = f"{self.agent_name}_{BENCHMARK_AGENT_NAME}_{self.benchmark_id}"
        benchmark_agent: dict[str, Any] = {
            "name": benchmark_agent_name,
            "wallet": copy.deepcopy(agent_wallet),
            "strategy": {"timed_events": [], "continuous_events": []},
        }

        # enrich the empty benchmark agent with the benchmark strategy
        self.strategy.create_benchmark_agent(
            benchmark_agent=benchmark_agent,
            benchmark_agent_name=benchmark_agent_name,
            block_number_start=block_number_start,
        )

        global_parameters["agents"].append(benchmark_agent)
