# Represents a wrapped event from the build_tx_payload() to be
# parsed in the execute_tx()

from typing import Any


class WrappedEvent:
    def __init__(
        self,
        action_type: str,
        protocol_id: str,
        protocol: Any,
        args: dict,
    ) -> None:
        self.action_type = action_type
        self.block_number = None
        self.protocol_id = protocol_id
        self.protocol = protocol
        self.args = args

    def map_tx(self) -> dict:
        tx_data = {
            "action_type": self.action_type,
            "block_number": -1,
            "protocol_id": self.protocol_id,
            "protocol": self.protocol,
        }
        tx_data.update(self.args)

        return tx_data

    def __str__(self) -> str:
        properties = [
            f"action_type: {self.action_type}",
            f"block_number: {self.block_number}",
            f"protocol_id: {self.protocol_id}",
            f"protocol: {self.protocol}",
            f"args: {self.args}",
        ]
        return "\n".join(properties)
