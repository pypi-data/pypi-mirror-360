from dataclasses import dataclass

from nqs_sdk_extension.run_configuration.protocol_parameters.protocol import SimulatedProtocolInformation
from nqs_sdk_extension.run_configuration.utils import TokenInfo
from nqs_sdk_extension.state import ABCProtocolState


@dataclass(kw_only=True)
class FakeStateCEX(ABCProtocolState):
    id: int
    name: str
    block_number: int
    block_timestamp: int


class CEXProtocolInformation(SimulatedProtocolInformation):
    def __init__(
        self,
        protocol_name: str,
        protocol_info: dict,
        id: int,
        block_number_start: int,
        timestamp_start: int,
        token_info_dict: dict[str, TokenInfo],
    ) -> None:
        super().__init__(
            protocol_name=protocol_name,
            id=id,
            block_number_start=block_number_start,
            timestamp_start=timestamp_start,
            protocol_info=protocol_info,
            random_generation_params=None,
            token_info_dict=token_info_dict,
        )
        self.initial_state: FakeStateCEX = FakeStateCEX(
            id=self.id, name=self.protocol_name, block_number=self.block_number_start, block_timestamp=0
        )

    def get_historical_state(self, historical_states: dict) -> ABCProtocolState:
        return self.initial_state

    def get_custom_state(self, custom_states: dict) -> ABCProtocolState:
        return self.initial_state
