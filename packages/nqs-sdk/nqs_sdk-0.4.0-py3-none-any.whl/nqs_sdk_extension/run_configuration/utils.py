import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import yaml

from nqs_sdk import BlockNumberOrTimestamp
from nqs_sdk_extension.spot import DataLoader
from nqs_sdk_extension.spot.utils import datetime64_to_timestamp

GENESIS_BLOCK_TS: int = 1438269973  # https://etherscan.io/block/0
DEFAULT_TOKEN_DECIMALS = 18
CTOKEN_DECIMALS = 8


@dataclass
class TokenInfo:
    decimals: int = DEFAULT_TOKEN_DECIMALS
    address: str = ""
    name: str = ""


@dataclass
class CTokenInfo(TokenInfo):
    underlying_symbol: str = ""
    underlying_address: str = ""
    comptroller_id: str = ""


@dataclass
class ScaledTokenInfo(TokenInfo):
    underlying_symbol: str = ""
    underlying_address: str = ""


def load_parameters_from_yaml(path_to_config: str) -> Any:
    """
    Loads parameters from yaml file
    :param path_to_config: Path to run configuration file
    :return: Dictionary of parameters
    """
    with open(path_to_config, "r") as file:
        params = yaml.safe_load(file)
    return params


def make_mapping_block_number_timestamp(
    block_start: Optional[int] = None,
    block_end: Optional[int] = None,
    timestamp_start: Optional[int] = None,
    timestamp_end: Optional[int] = None,
) -> dict[int, int]:
    if DataLoader.quantlib_source().source() is None:
        raise ValueError("Source not set on DataLoader...")

    if block_start is not None:
        begin: BlockNumberOrTimestamp = BlockNumberOrTimestamp.block_number(block_start)
        end: BlockNumberOrTimestamp | None = (
            BlockNumberOrTimestamp.block_number(block_end) if block_end is not None else None
        )
    elif timestamp_start is not None:
        begin = BlockNumberOrTimestamp.timestamp(timestamp_start)
        end = BlockNumberOrTimestamp.timestamp(timestamp_end) if timestamp_end is not None else None
    else:
        raise ValueError("Begin timestamp or block cannot be None")

    result = DataLoader.quantlib_source().blocks_from_interval("Ethereum", begin, end)
    mapping_block_number_timestamp: dict[int, int] = {
        int(key): int(value) for key, value in zip(result["number"], result["timestamp"])
    }

    # check if our timestamp_end is in the future
    latest_retrieved_timestamp = int(result["timestamp"][-1])
    latest_retrieved_block_number = int(result["number"][-1])
    first_retrieved_timestamp = int(result["timestamp"][0])
    if timestamp_end is not None and timestamp_end > latest_retrieved_timestamp + 12:
        # then need to complete with synthetic data
        mapping_to_append = make_regular_mapping_block_number_timestamp(
            timestamp_start=latest_retrieved_timestamp + 12,
            timestamp_end=timestamp_end,
            use_genesis=False,
            timestamp_reference=latest_retrieved_timestamp + 12,
            block_number_reference=latest_retrieved_block_number + 1,
        )
        mapping_block_number_timestamp.update(mapping_to_append)
    elif block_end is not None and block_end > latest_retrieved_block_number:
        raise NotImplementedError("Case based on block numbers not yet implemented...")

    if timestamp_start is not None and timestamp_start < first_retrieved_timestamp:
        first_block = min((mapping_block_number_timestamp.keys()))
        mapping_block_number_timestamp[first_block] = timestamp_start

    return mapping_block_number_timestamp


def make_regular_mapping_block_number_timestamp(
    block_start: Optional[int] = None,
    block_end: Optional[int] = None,
    timestamp_start: Optional[int] = None,
    timestamp_end: Optional[int] = None,
    block_spacing: int = 12,
    use_genesis: bool = True,
    timestamp_reference: int | None = None,
    block_number_reference: int | None = None,
) -> dict[int, int]:
    """
    Dummy mapping where blocks are regularly separated by block_spacing seconds
    """
    mapping_block_number_timestamp: dict[int, int]

    if block_start is None and block_end is None:
        assert timestamp_start is not None, "timestamp_start must be set"
        assert timestamp_end is not None, "timestamp_end must be set"
        # timestamp mode
        mapping_block_number_timestamp = {
            get_block_of_timestamp(
                timestamp,
                block_spacing=block_spacing,
                use_genesis=use_genesis,
                timestamp_reference=timestamp_reference,
                block_number_reference=block_number_reference,
            ): timestamp
            for timestamp in range(timestamp_start, timestamp_end + 1, block_spacing)
        }

    elif timestamp_start is None and timestamp_end is None:
        assert block_start is not None, "block_start must be set"
        assert block_end is not None, "block_end must be set"
        # block mode
        mapping_block_number_timestamp = {
            block: get_timestamp_of_block(block, block_spacing=block_spacing, force_dummy=True)
            for block in range(block_start, block_end + 1)
        }
    else:
        raise ValueError("Please provide either a block range or a timestamp range to the simulation...")

    return mapping_block_number_timestamp


def set_mapping_block_number_timestamp(
    block_number_start: Optional[int] = None,
    block_number_end: Optional[int] = None,
    timestamp_start: Optional[int] = None,
    timestamp_end: Optional[int] = None,
) -> dict[int, int]:
    try:
        mapping_block_number_timestamp = make_mapping_block_number_timestamp(
            block_start=block_number_start,
            block_end=block_number_end,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )
    except Exception as e:
        if os.getenv("FALLBACK_DUMMY_MAPPING", None) not in (1, True, "1", "True"):
            raise e
        logging.error(f"{e} - falling back to dummy mapping")
        mapping_block_number_timestamp = make_regular_mapping_block_number_timestamp(
            block_start=block_number_start,
            block_end=block_number_end,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )
    return mapping_block_number_timestamp


def get_timestamp_of_block(block: int, block_spacing: int = 12, force_dummy: bool = False) -> int:
    """
    Gets the timestamp corresponding to the block, if that is in the past, otherwise a timestamp generated assuming
    blocks are separated by block_spacing seconds
    :param block:
    :param block_spacing:
    :return:
    """
    source = DataLoader.quantlib_source()
    if source.source() is not None and not force_dummy:
        b = BlockNumberOrTimestamp.block_number(block)
        result = source.blocks_from_interval("Ethereum", b, b)

        if len(result["timestamp"]) > 0:
            return datetime64_to_timestamp(result["timestamp"])

    return GENESIS_BLOCK_TS + block * block_spacing


def get_block_of_timestamp(
    timestamp: int,
    block_spacing: int = 12,
    use_genesis: bool = True,
    timestamp_reference: int | None = None,
    block_number_reference: int | None = None,
) -> int:
    """
    Gets the block corresponding to the timestamp, if that is in the past, otherwise a block generated assuming
    blocks are separated by block_spacing seconds
    :param timestamp:
    :param source:
    :param block_spacing:
    :return:
    """
    if use_genesis:
        time_since_genesis = timestamp - GENESIS_BLOCK_TS
        block_number_reference = 1
    else:
        if timestamp_reference is None:
            raise ValueError("Invalid reference timestamp...")
        elif block_number_reference is None:
            raise ValueError("Invalid reference block number...")
        time_since_genesis = timestamp - timestamp_reference

    if time_since_genesis < 0:
        raise ValueError("Provide a simulation after Ethereum genesis...")
    return time_since_genesis // block_spacing + block_number_reference
