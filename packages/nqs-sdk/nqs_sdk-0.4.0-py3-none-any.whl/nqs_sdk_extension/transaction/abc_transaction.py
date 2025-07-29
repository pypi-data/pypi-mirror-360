from dataclasses import dataclass
from enum import Enum
from typing import Optional

from nqs_pycore import Wallet


@dataclass(kw_only=True)
class ABCTransaction:
    action_type: Enum
    block_number: int
    block_index: int = -1  # transaction position in the block
    block_timestamp: int = -1  # shall be injected by broker inside the transaction obj
    protocol_id: str
    sender_wallet: Optional[Wallet]
    action_name: Optional[str] = None  # the name of the action from conf file - for logging uses

    def time_index(self) -> int:
        return self.block_number

    def inject_block_timestamp(self, block_timestamp: int) -> None:
        self.block_timestamp = block_timestamp
