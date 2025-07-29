# mypy: disable-error-code="return"
import logging
import os
import re
from enum import Enum
from typing import Any, Literal, Tuple

import numpy as np

from nqs_sdk_extension.config_utils.benchmark import Benchmark
from nqs_sdk_extension.constants import BENCHMARK_AGENT_NAME, DEFAULT_N_METRIC_OBSERVATIONS
from nqs_sdk_extension.mappings import mapping_type_to_generator, mapping_type_to_protocol_info
from nqs_sdk_extension.run_configuration.protocol_parameters.protocol import SimulatedProtocolInformation
from nqs_sdk_extension.run_configuration.utils import TokenInfo, set_mapping_block_number_timestamp
from nqs_sdk_extension.token_utils import TOKENS_TO_WRAP, wrap_token

RESERVED_SUFFIX_PATTERN = r"_#\d+$"
ALLOWED_AGENTS_KEYS = {"name", "wallet", "strategy", "benchmarks"}


class Parameters:
    def __init__(
        self, execution_mode: Literal["backtest", "simulation"], global_parameters: dict, **kwargs: Any
    ) -> None:
        self._validate(execution_mode)
        self.execution_mode = execution_mode
        self.common_parameters = CommonParameters(global_parameters, kwargs.get("output_path", ""))
        self.backtest_parameters = (
            BacktestParameters(global_parameters, common_parameters=self.common_parameters)
            if execution_mode == "backtest"
            else None
        )
        self.simulation_parameters = (
            SimulationParameters(global_parameters, common_parameters=self.common_parameters)
            if execution_mode == "simulation"
            else None
        )
        self.spot_parameters = SpotParameters(global_parameters, self.execution_mode)
        self.agents_parameters = agent_helper(
            global_parameters.get("agents", []) if global_parameters.get("agents", []) is not None else [{}]
        )
        self._check_benchmarks_validity(self.common_parameters.benchmarks, self.spot_parameters.tokens)

    @staticmethod
    def _validate(execution_mode: Literal["backtest", "simulation"]) -> None:
        if execution_mode not in ["simulation", "backtest"]:
            raise ValueError("Execution mode must be either simulation or backtest")

    @staticmethod
    def _check_benchmarks_validity(benchmarks: list[Benchmark], token_data: list[str]) -> None:
        """
        Check that the benchmarks are valid.
        """
        for benchmark in benchmarks:
            for token in benchmark.strategy.tokens_used_in_benchmark:
                if token not in token_data:
                    raise ValueError(f"Token {token} used in benchmark {benchmark.agent_name} is not in the spot data.")


class SpotTypes(Enum):
    """Enum to represent the different types of spots."""

    GBM = "GBM"
    WGN = "WGN"
    OU = "OU"
    HISTORICAL = "historical"
    CUSTOM = "custom"


class SpotParameters:
    def __init__(self, global_parameters: dict, execution_mode: Literal["backtest", "simulation"]) -> None:
        self._global_parameters = global_parameters
        self.stochastic_param: dict = {}
        self.deterministic_params: dict = {}
        if self._global_parameters.get("spot", None) is not None:
            self.stochastic_param, self.deterministic_params = self.get_stoch_det_params(execution_mode)
            self.correlation = self._global_parameters["spot"].get("correlation", np.array([[1]]))

    def get_stoch_det_params(self, execution_mode: Literal["backtest", "simulation"]) -> Tuple[dict, dict]:
        stoc_spots = {}
        det_spots = {}
        for spot in self._global_parameters["spot"]["spot_list"]:
            pair = spot.pop("name")
            tuple_pair = tuple(pair.split("_"))
            process_type = list(spot.keys())[0]
            if execution_mode == "backtest" and process_type != SpotTypes.HISTORICAL.value:
                logging.warning(
                    f"{process_type} process not supported in backtest mode. Only historical processes "
                    f"are allowed. The process will be automatically set to historical"
                )
                process_type = SpotTypes.HISTORICAL.value
                spot = {process_type: {}}
            if len(tuple_pair) != 2:
                raise ValueError(f"{pair} is not an accepted spot pair format. The accepted format is TOKEN0_TOKEN1")
            if process_type in [SpotTypes.GBM.value, SpotTypes.WGN.value, SpotTypes.OU.value]:
                stoc_spots[tuple_pair] = spot
            elif process_type in [SpotTypes.CUSTOM.value, SpotTypes.HISTORICAL.value]:
                det_spots[tuple_pair] = spot
            else:
                raise ValueError(
                    f"Unknown process type {process_type}. Known types are GBM, WGN, OU, " f"historical, custom"
                )
        return stoc_spots, det_spots

    @property
    def tokens(self) -> list[str]:
        tokens = []
        for token0, token1 in list(self.stochastic_param.keys()) + list(self.deterministic_params.keys()):
            tokens.append(wrap_token(token0))
            tokens.append(wrap_token(token1))
        return list(set(tokens))


class CommonParameters:
    def __init__(self, global_parameters: dict, output_path: str) -> None:
        # time / block settings
        tmp_block_number_start: int | None = global_parameters["common"].get("block_number_start", None)
        tmp_block_number_end: int | None = global_parameters["common"].get("block_number_end", None)
        tmp_timestamp_start: int | None = global_parameters["common"].get("timestamp_start", None)
        tmp_timestamp_end: int | None = global_parameters["common"].get("timestamp_end", None)
        self._validate(
            block_number_start=tmp_block_number_start,
            block_number_end=tmp_block_number_end,
            timestamp_start=tmp_timestamp_start,
            timestamp_end=tmp_timestamp_end,
        )
        self._mapping_block_number_timestamp: dict[int, int] = set_mapping_block_number_timestamp(
            block_number_start=tmp_block_number_start,
            block_number_end=tmp_block_number_end,
            timestamp_start=tmp_timestamp_start,
            timestamp_end=tmp_timestamp_end,
        )
        simulation_length = self.block_number_end - self.block_number_start
        default_block_step_metrics = max(1, simulation_length // DEFAULT_N_METRIC_OBSERVATIONS)
        self.block_step_metrics: int = global_parameters["common"].get("block_step_metrics", default_block_step_metrics)
        self.gas_fee: float = global_parameters["common"].get("gas_fee", 0.0)

        self.numeraire: str = global_parameters["common"]["numeraire"]
        self.gas_fee_ccy: str | None = (
            wrap_token(global_parameters["common"].get("gas_fee_ccy")) if self.gas_fee > 0 else None
        )
        self.mandatory_tokens: list[str] = global_parameters["common"].get("mandatory_tokens", [])
        # add gas_fee_ccy to mandatory_tokens
        if self.gas_fee_ccy is not None and self.gas_fee_ccy not in self.mandatory_tokens:
            self.mandatory_tokens += [self.gas_fee_ccy]

        self.plot_output: bool = global_parameters["common"].get("plot_output", False)
        self.save_metrics: bool = global_parameters["common"].get("save_metrics", False)
        self.use_arbitrageur: bool = global_parameters["common"].get("arbitrage_block_frequency", 0) > 0.0
        self.arbitrage_block_frequency: int | None = global_parameters["common"].get("arbitrage_block_frequency", None)
        directory = os.path.dirname(output_path)
        if self.save_metrics and not os.path.exists(directory):
            raise ValueError(
                f"The provided path for metric output is invalid...\nDirectory {directory} does not exist..."
            )
        self.output_path = output_path
        self.agents = global_parameters.get("agents", []) if global_parameters.get("agents") is not None else []
        self.benchmarks: list[Benchmark] = self.create_benchmarks()
        self.add_benchmarks_to_agents(global_parameters=global_parameters, block_number_start=self.block_number_start)

    def create_benchmarks(self) -> list[Benchmark]:
        list_benchmarks = []

        for agent in self.agents:
            agent_name = agent["name"]
            benchmark_id = 0
            for benchmark_config in agent.get("benchmarks", []):
                list_benchmarks.append(
                    Benchmark(agent_name=agent_name, benchmark_config=benchmark_config, benchmark_id=benchmark_id)
                )
                benchmark_id += 1
        return list_benchmarks

    def add_benchmarks_to_agents(self, global_parameters: dict, block_number_start: int) -> None:
        """
        @notice Includes the benchmark object to the list of agents for the simulation
        @param global_parameters The so-called global parameters defined by user in
        """
        mapping_agent_wallet: dict = {el["name"]: el["wallet"] for el in self.agents}
        for benchmark in self.benchmarks:
            agent = benchmark.agent_name
            if BENCHMARK_AGENT_NAME in agent:
                raise ValueError(f"Invalid agent name: {agent}...\nShould not contain {BENCHMARK_AGENT_NAME}...")
            agent_wallet: dict = mapping_agent_wallet[agent]
            benchmark.add_benchmark_agent(
                global_parameters=global_parameters, agent_wallet=agent_wallet, block_number_start=block_number_start
            )

    @staticmethod
    def _validate(
        block_number_start: int | None,
        block_number_end: int | None,
        timestamp_start: int | None,
        timestamp_end: int | None,
    ) -> None:
        """
        Validate that either blocks or timestamps are set. In case both are set, raise an error.
        """
        blocks_are_set = block_number_start is not None and block_number_end is not None
        timestamps_are_set = timestamp_start is not None and timestamp_end is not None
        if blocks_are_set and timestamps_are_set:
            raise ValueError(
                "Both blocks and timestamps are used to instantiate the simulation. "
                "Please correct this by providing the data only for block numbers or timestamps."
            )
        elif not blocks_are_set and not timestamps_are_set:
            raise ValueError("Please provide at least blocks or timestamps...")

    @property
    def block_number_start(self) -> int:
        return min(self._mapping_block_number_timestamp.keys())

    @property
    def block_number_end(self) -> int:
        return max(self._mapping_block_number_timestamp.keys())

    @property
    def timestamp_start(self) -> int:
        return min(self._mapping_block_number_timestamp.values())

    @property
    def timestamp_end(self) -> int:
        return max(self._mapping_block_number_timestamp.values())

    @property
    def mapping_block_number_timestamp(self) -> dict[int, int]:
        return self._mapping_block_number_timestamp


class BacktestParameters:
    def __init__(self, global_parameters: dict, common_parameters: CommonParameters) -> None:
        self._global_parameters = global_parameters
        if self._global_parameters.get("backtest_environment", None) is not None:
            self.block_number_start = common_parameters.block_number_start
            self.block_number_end = common_parameters.block_number_end
            self.timestamp_start = common_parameters.timestamp_start
            self.timestamp_end = common_parameters.timestamp_end
            self.token_mapping = self._global_parameters["backtest_environment"]["token_addresses"]
            self._validate()
            self._fill_protocols_to_replay()

    def _fill_protocols_to_replay(self) -> None:
        self.protocols_to_replay: dict[str, BacktestedProtocolInformation] = {}
        for protocol_name, protocol_info in self._global_parameters["backtest_environment"][
            "protocols_to_replay"
        ].items():
            if protocol_name in ["uniswap_v3"]:
                for pool_info in protocol_info["pools"]:
                    pool_name = pool_info.pop("pool_name")
                    pool_info = {protocol_name: pool_info}
                    self.protocols_to_replay[pool_name] = BacktestedProtocolInformation(
                        protocol_name=pool_name, protocol_info=pool_info, id=len(self.protocols_to_replay)
                    )
            else:
                self.protocols_to_replay[protocol_name] = BacktestedProtocolInformation(
                    protocol_name=protocol_name,
                    protocol_info={protocol_name: protocol_info},
                    id=len(self.protocols_to_replay),
                )

    def _validate(self) -> None:
        pass

    @property
    def token_symbols(self) -> list[str]:
        return list(self.token_mapping.keys())

    @property
    def token_addresses(self) -> list[str]:
        return list(self.token_mapping.values())


class SimulationParameters:
    def __init__(self, global_parameters: dict, common_parameters: CommonParameters) -> None:
        self._global_parameters = global_parameters
        if self._global_parameters.get("simulation_environment", None) is not None:
            self.block_number_start = common_parameters.block_number_start
            self.block_number_end = common_parameters.block_number_end
            self.timestamp_start = common_parameters.timestamp_start
            self.timestamp_end = common_parameters.timestamp_end
            self._validate()
            self.protocols_to_simulate: dict[str, SimulatedProtocolInformation] = {}
            self.calibrated_params_path_dict: dict[str, str] = {}
            self.token_info_dict: dict[str, TokenInfo] = self.build_token_info(
                self._global_parameters["simulation_environment"].get("tokens_info", None)
            )
            self._fill_protocols_to_simulate()

    def _fill_protocols_to_simulate(self) -> None:
        for protocol_name, protocol_info in self._global_parameters["simulation_environment"][
            "protocols_to_simulate"
        ].items():
            initial_state = protocol_info["initial_state"]
            type_state = list(initial_state.keys())[0]
            if protocol_name in ["uniswap_v3"]:
                for pool_info in initial_state[type_state]["pools"]:
                    pool_name = pool_info["pool_name"]
                    random_generation_params = [
                        x for x in protocol_info["random_generation_params"]["pools"] if x["pool_name"] == pool_name
                    ][0]
                    parsing_info = {
                        protocol_name: {
                            "initial_state": {type_state: pool_info},
                            "random_generation_params": random_generation_params,
                        }
                    }
                    self.protocols_to_simulate[pool_name] = parse_protocol_info(
                        protocol_name=pool_name,
                        protocol_info=parsing_info,
                        id=len(self.protocols_to_simulate),
                        block_number_start=self.block_number_start,
                        timestamp_start=self.timestamp_start,
                        token_info_dict=self.token_info_dict,
                    )
            else:
                self.protocols_to_simulate[protocol_name] = parse_protocol_info(
                    protocol_name=protocol_name,
                    protocol_info={protocol_name: protocol_info},
                    id=len(self.protocols_to_simulate),
                    block_number_start=self.block_number_start,
                    timestamp_start=self.timestamp_start,
                    token_info_dict=self.token_info_dict,
                )
                if self.protocols_to_simulate[protocol_name].calibrated_params_path is not None:
                    self.calibrated_params_path_dict[protocol_name] = self.protocols_to_simulate[
                        protocol_name
                    ].calibrated_params_path

    def set_calibrated_parameters(self, calibrated_parameters: dict[str, Any]) -> None:
        for protocol_name in self.calibrated_params_path_dict.keys():
            self.protocols_to_simulate[protocol_name].random_generation_params = calibrated_parameters[protocol_name]

    def _validate(self) -> None:
        """
        Validate that timestamp and block ranges are set
        """
        assert self.block_number_start is not None, "Simulation starting block is not defined..."
        assert self.block_number_end is not None, "Simulation ending block is not defined..."
        assert self.timestamp_start is not None, "Simulation starting timestamp is not defined..."
        assert self.timestamp_end is not None, "Simulation ending timestamp is not defined..."

    @staticmethod
    def build_token_info(token_info_param: dict | None) -> dict[str, TokenInfo]:
        token_info_dict: dict[str, TokenInfo] = {}
        if token_info_param is None:
            return token_info_dict
        for token in token_info_param:
            address = token_info_param[token].get("address", "0x" + token)
            # the decimals field is mandatory in the schema
            decimals = token_info_param[token].get("decimals")
            token_info_dict[wrap_token(token)] = TokenInfo(decimals=decimals, address=address)
        return token_info_dict


class BacktestedProtocolInformation:
    def __init__(self, protocol_name: str, protocol_info: dict, id: int) -> None:
        self.protocol_name = protocol_name
        if len(protocol_info.keys()) != 1:
            raise ValueError(
                f"Wrong configuration for protocol {protocol_name}. Only one protocol type should be" f" specified"
            )
        self.protocol_type = list(protocol_info.keys())[0]
        if self.protocol_type not in mapping_type_to_generator.keys():
            raise ValueError(
                f"Wrong protocol type. Got {self.protocol_type}, expected one of "
                f"{list(mapping_type_to_generator.keys())}"
            )
        self.protocol_info = protocol_info[self.protocol_type]
        self.id = id


def agent_helper(agents_list: list[dict]) -> dict[str, dict]:
    agents_dict: dict = {}
    uniswap_agent_tokenid_mapping: dict[str, list[str]] = {}
    for agent_dict in agents_list:
        if not set(agent_dict.keys()).issubset(ALLOWED_AGENTS_KEYS):
            raise ValueError(
                f"Agent {agent_dict['name']} has invalid keys in the configuration: "
                f"{set(agent_dict.keys()) - ALLOWED_AGENTS_KEYS}"
            )
        agents_dict[agent_dict["name"]] = {}
        agent_info = agents_dict[agent_dict["name"]]
        if agent_dict.get("wallet", None) is not None:
            agent_info["wallet"] = handle_wallet(agent_dict["wallet"])
            agent_info["strategy"] = agent_dict.get("strategy", {})
            for key, events in agent_info["strategy"].items():
                if key == "custom_variables":
                    continue
                for event in events:
                    actions = event.get("actions", [])
                    for action in actions:
                        action = wrap_tokens_actions(action)
                        update_uniswap_tokenid_mapping(agent_dict["name"], action, uniswap_agent_tokenid_mapping)
    check_uniswap_tokenid_mapping(uniswap_agent_tokenid_mapping)
    return agents_dict


def handle_wallet(agent_dict_wallet: dict) -> dict:
    agent_info_wallet = {}
    for token, amount in agent_dict_wallet.items():
        try:
            float_amount = float(amount)
            if float_amount < 0:
                raise ValueError(f"Amount {amount} for token {token} is negative")
            agent_info_wallet[wrap_token(token)] = float_amount
        except ValueError:
            raise ValueError(f"Amount {amount} for token {token} is not a valid number")
    return agent_info_wallet


def update_uniswap_tokenid_mapping(
    agent_name: str, action: dict, uniswap_agent_tokenid_mapping: dict[str, list[str]]
) -> None:
    # This only works because token_id is an argument used only in UniswapV3
    action_args = action.get("args", {})
    agent_token_ids = uniswap_agent_tokenid_mapping.get(agent_name, [])
    for arg in action_args:
        if arg == "token_id":
            if re.search(RESERVED_SUFFIX_PATTERN, action_args["token_id"]):
                raise ValueError(f"Token id {action_args['token_id']} is using a reserved suffix _#.")
            agent_token_ids.append(action_args["token_id"])
    uniswap_agent_tokenid_mapping[agent_name] = agent_token_ids


def check_uniswap_tokenid_mapping(uniswap_agent_tokenid_mapping: dict[str, list[str]]) -> None:
    # two agents cannot have the same token_id
    token_id_mapping: dict[str, str] = {}
    for agent, token_ids in uniswap_agent_tokenid_mapping.items():
        for token_id in set(token_ids):
            if token_id in token_id_mapping:
                agents = [agent, token_id_mapping[token_id]]
                agents.sort()
                raise ValueError(f"Token id {token_id} is used by multiple agents: {agents[0]} and {agents[1]}")
            token_id_mapping[token_id] = agent


def wrap_tokens_actions(action: dict) -> dict:
    for token in TOKENS_TO_WRAP:
        # replace token with wrapped token when it is preceded by a quote, a double-quote, a slash or at the
        # beginning of the string
        pattern = rf"(?:(?<=[\"'/])|^){token}"
        if not action.get("condition", None):
            continue
        action["condition"] = re.sub(pattern, wrap_token(token), action.get("condition"))  # type: ignore
        for arg, value in action.get("args", {}).items():
            if isinstance(value, str):
                action["args"][arg] = re.sub(pattern, wrap_token(token), value)
    return action


def parse_protocol_info(
    protocol_name: str,
    protocol_info: dict,
    id: int,
    block_number_start: int,
    timestamp_start: int,
    token_info_dict: dict[str, TokenInfo],
) -> Any:
    for protocol_type, protocol_config in protocol_info.items():
        protocol_config.update({"protocol_type": protocol_type})
        if mapping_type_to_protocol_info.get(protocol_type, None) is not None:
            return mapping_type_to_protocol_info[protocol_type](
                protocol_name=protocol_name,
                id=id,
                block_number_start=block_number_start,
                timestamp_start=timestamp_start,
                protocol_info=protocol_config,
                token_info_dict=token_info_dict,
            )
        else:
            raise NotImplementedError(f"Protocol type {protocol_type} is not implemented")
