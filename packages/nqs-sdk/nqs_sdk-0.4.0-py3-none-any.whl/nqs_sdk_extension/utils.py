import calendar
import datetime
import logging
import os
import re
from abc import ABC
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

import numpy as np

MAX_BYTES_LOG_FILE = 50_000_000  # Max size of log file in bytes
BACKUP_COUNT_LOG_FILE = 20  # Number of backup log files


class StartsWithFilter(logging.Filter):
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix

    def filter(self, record: Any) -> bool:
        if record.getMessage().startswith(self.prefix):
            return True
        else:
            return False


def setup_logging(filename: str, level: str, startswith: Optional[str] = None) -> None:
    # Configure logging for the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.getLevelName(level))  # Set the root logger level

    # Remove the log file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    # Create a file handler for the root logger
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=filename, maxBytes=MAX_BYTES_LOG_FILE, backupCount=BACKUP_COUNT_LOG_FILE
    )
    file_handler.setLevel(logging.getLevelName(level))  # Set the file handler level
    if startswith:
        prefix_filter = StartsWithFilter("Key:")
        file_handler.addFilter(prefix_filter)  # Add filter to the file handler

    # Create a formatter for the file handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def load_log_file(filename: str, agent_name: str, key: str) -> List[str]:
    """
    Load a log file and return the lines that contain the agent name and key.
    """
    with open(filename, "r") as file:
        log_lines = file.readlines()
    agent_log_lines = [line for line in log_lines if "Agent: " + agent_name in line and "Key: " + key in line]
    return agent_log_lines


def parse_tx_log(tx_log: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parse a transaction log line and return the timestamp and a dictionary with the transaction details
    """
    pattern = r"Timestamp: (\d+)"
    match = re.search(pattern, tx_log)
    if match:
        timestamp = match.group(1)
    else:
        raise ValueError("No timestamp found in the string.")

    pattern = r"Transaction: (.+?) -"
    match = re.search(pattern, tx_log)
    if match:
        tx_name = match.group(1)
    else:
        raise ValueError("No transaction name found in the string.")

    pattern = r"Protocol: (.+?):"
    match = re.search(pattern, tx_log)
    if match:
        protocol_name = match.group(1)
    else:
        raise ValueError("No protocol name found in the string.")

    pattern = r"Comment: (.+)"
    match = re.search(pattern, tx_log)
    if match:
        comment = match.group(1)
    else:
        raise ValueError("No comment found in the string.")

    return timestamp, {"tx_name": tx_name, "protocol_name": protocol_name, "comment": comment}


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    items: List[Tuple[str, str]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_today_tms() -> int:
    return int(calendar.timegm(datetime.date.today().timetuple()))


def get_datehour_tms() -> int:
    return get_today_tms() + 3600 * (datetime.datetime.now().hour - 1)


T = TypeVar("T", bound="AbstractDataclass")


@dataclass
class AbstractDataclass(ABC):
    @classmethod
    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)


def generate_grid(block_number_start: int, block_number_end: int, block_step_observables: int) -> List[int]:
    """Generate a grid of block numbers to sample observables."""
    return list(range(block_number_start, block_number_end, block_step_observables))


def sample_outputs(observables: dict[str, Any], timestamps_grid: List[int]) -> dict[str, Any]:
    """Sample observables at given timestamps."""
    sampled_observables = {}
    for metric, values in observables.items():
        if metric.startswith("events_log_"):
            sampled_observables[metric] = values
            continue
        sampled_observables[metric] = {
            "block_timestamps": timestamps_grid,
            "values": forward_flat_interpolator(values["block_timestamps"], values["values"], timestamps_grid),
        }
    return sampled_observables


def forward_flat_interpolator(x: List[int], y: List[float], x_new: List[int]) -> List[float]:
    """
    Forward flat interpolator function for multiple target x values using NumPy.

    Parameters:
    - x: List of x values.
    - y: List of y values.
    - x_new: List of target x values for interpolation.

    Returns:
    - interpolated_y_values: List of interpolated y values.
    """
    # Ensure the input lists are of the same length
    if len(x) != len(y):
        raise ValueError("Input lists must have the same length.")

    # Convert input lists to NumPy arrays for efficient calculations
    x_arr = np.array(x)
    y_arr = np.array(y)
    x_new_arr = np.array(x_new)

    # Find the indices of the previous x value for each target x value
    closest_indices = np.searchsorted(x_arr, x_new_arr, side="right") - 1

    def fetch_y_value(idx: int) -> float:
        return np.nan if idx == -1 else float(y_arr[idx])

    # Retrieve the corresponding y values using the indices
    interpolated_y_values = [fetch_y_value(idx) for idx in closest_indices]

    return interpolated_y_values


if __name__ == "__main__":
    y_new = forward_flat_interpolator([1, 3, 5], [1, 2, 3], [0, 2, 4, 6])
    assert y_new == [np.nan, 1.0, 2.0, 3.0]
