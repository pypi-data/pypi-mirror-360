import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from nqs_sdk_extension.run_configuration.utils import DEFAULT_TOKEN_DECIMALS, TokenInfo
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.token_utils import TOKEN_DECIMALS


class SimulatedProtocolInformation(ABC):
    """Abstract class to represent the information of a protocol to simulate.
    This information come from the parameter file."""

    def __init__(
        self,
        protocol_name: str,
        id: int,
        block_number_start: int,
        timestamp_start: int,
        protocol_info: dict,
        token_info_dict: dict[str, TokenInfo],
        random_generation_params: Optional[dict] = None,
        additional_parameters: Optional[dict] = None,
    ) -> None:
        self.block_number_start = block_number_start
        self.timestamp_start = timestamp_start
        self.id = id
        self.protocol_type = protocol_info["protocol_type"]
        self.protocol_name = protocol_name
        self.token_info_dict = token_info_dict
        if random_generation_params is None:
            random_generation_params = {}
        self.random_generation_params = random_generation_params
        self.calibrated_params_path = self.random_generation_params.get("calibrated_params_path", None)
        if additional_parameters is None:
            additional_parameters = {}
        self.additional_parameters = additional_parameters
        self.initial_state: Any = None

    def get_token_info(self, token: str) -> TokenInfo:
        if token not in self.token_info_dict:
            logging.warning(
                f"Using the default attributes "
                f"for {token} as no input has been provided: "
                f"decimals={TOKEN_DECIMALS.get(token, DEFAULT_TOKEN_DECIMALS)}, address=0x{token}"
            )
            self.token_info_dict[token] = TokenInfo(
                decimals=TOKEN_DECIMALS.get(token, DEFAULT_TOKEN_DECIMALS), address="0x" + token, name=token + "coin"
            )
        return self.token_info_dict[token]

    def set_token_info(self, token: str, decimals: int, address: str) -> None:
        if token in self.token_info_dict:
            # check only differences on decimals for the moment
            if decimals != self.token_info_dict[token].decimals:
                raise ValueError(
                    f"The {token} decimals obtained from the Smart Contract"
                    f"are {decimals}, which is different from "
                    f"what has been set before ({self.token_info_dict[token].decimals})"
                )
        else:
            self.token_info_dict[token] = TokenInfo(decimals=decimals, address=address, name=token + "coin")

    @abstractmethod
    def get_custom_state(self, custom_states: dict) -> ABCProtocolState:
        pass

    @abstractmethod
    def get_historical_state(self, historical_states: dict) -> ABCProtocolState:
        pass
