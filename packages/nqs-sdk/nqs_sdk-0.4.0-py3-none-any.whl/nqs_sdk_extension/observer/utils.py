import re
from abc import ABC
from dataclasses import dataclass
from enum import Enum

import numpy as np


class MetricType(Enum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


@dataclass
class MetricInfo(ABC):
    name: str
    type: MetricType = MetricType.CONTINUOUS
    lower_bound: int | float = 0.0
    upper_bound: int | float = np.inf
    default: int | float = 0.0


def reverse_mapping(my_dict: dict) -> dict:
    """
    Inverse keys and values from dict my_dict, effectively reversing the mapping. Assumes bidirectional mapping.
    """
    return {value: key for key, value in my_dict.items()}


def make_metric_name(
    protocol: str,
    metric: str,
    agent: str | None = None,
    position: str | None = None,
    token: str | None = None,
    window: str | None = None,
    pair: str | None = None,
) -> str:
    left_part = (f"{agent}." if agent is not None else "") + f"{protocol}.{metric}"
    right_part = []
    if token is not None:
        right_part.append(f'token="{token}"')
    if pair is not None:
        right_part.append(f'pair="{pair}"')
    if position is not None:
        right_part.append(f'position="{position}"')
    if window is not None:
        right_part.append(f'window="{window}"')
    if right_part:
        return left_part + f":{{{','.join(right_part)}}}"
    else:
        return left_part


def make_metric_info(
    protocol: str,
    metric: str,
    agent: str | None = None,
    position: str | None = None,
    token: str | None = None,
    window: str | None = None,
    pair: str | None = None,
    metric_type: MetricType = MetricType.CONTINUOUS,
    upper_bound: float | int = np.inf,
    lower_bound: float | int = 0.0,
) -> MetricInfo:
    return MetricInfo(
        make_metric_name(protocol, metric, agent, position, token, window, pair), metric_type, lower_bound, upper_bound
    )


def parse_metric_name(metric_name: str) -> dict:
    match = re.match(r"((?P<agent>\w+)\.)?(?P<protocol>\w+)\.(?P<metric>\w+)(:{(?P<args>.*)})?", metric_name)
    if match is None:
        raise ValueError(f"Invalid metric name: {metric_name}")
    result = match.groupdict()
    if result["args"] is not None:
        args = result["args"].split(",")
        for arg in args:
            key, value = arg.split("=")
            result[key] = value.strip('"')
    result.pop("args")
    return result


def prefix_agent_to_metric_name(metric_name_str: str, agent: str) -> str:
    parsed_metric = parse_metric_name(metric_name_str)
    if "agent" in parsed_metric and parsed_metric["agent"] is not None:
        raise ValueError(f"Metric name {metric_name_str} already contains an agent")
    parsed_metric["agent"] = agent
    return make_metric_name(
        parsed_metric["protocol"],
        parsed_metric["metric"],
        parsed_metric["agent"],
        parsed_metric.get("position"),
        parsed_metric.get("token"),
        parsed_metric.get("window"),
    )


def add_position_to_metric_name(metric_name_str: str, position: str) -> str:
    parsed_metric = parse_metric_name(metric_name_str)
    if "position" in parsed_metric and parsed_metric["position"] is not None:
        raise ValueError(f"Metric name {metric_name_str} already contains a position")
    parsed_metric["position"] = position
    return make_metric_name(
        parsed_metric["protocol"],
        parsed_metric["metric"],
        parsed_metric.get("agent"),
        parsed_metric["position"],
        parsed_metric.get("token"),
        parsed_metric.get("window"),
    )


def remove_agent_from_metric_name(metric_name_str: str) -> str:
    parsed_metric = parse_metric_name(metric_name_str)
    parsed_metric.pop("agent", None)
    return make_metric_name(
        parsed_metric["protocol"],
        parsed_metric["metric"],
        None,  # agent = None
        parsed_metric.get("position"),
        parsed_metric.get("token"),
        parsed_metric.get("window"),
        parsed_metric.get("pair"),
    )


def is_valid_metric_name(metric_name: str) -> bool:
    match = re.match(r"((?P<agent>\w+)\.)?(?P<protocol>\w+)\.(?P<metric>\w+)(:{(?P<args>.*)})?", metric_name)
    return match is not None
