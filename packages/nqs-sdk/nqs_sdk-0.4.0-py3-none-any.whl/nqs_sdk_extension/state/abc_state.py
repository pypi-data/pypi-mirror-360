from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass(kw_only=True)
class ABCProtocolState(ABC):
    """
    A class representing the state of a protocol at a specific point in time.

    Attributes:
        id (int): the id of the protocol
        name (str): the name of the protocol
        block_number (int): the block number for the requested snapshot
        timestamp (int): the corresponding timestamp for the block number
    """

    id: int
    name: str
    block_number: int
    block_timestamp: int

    def __lt__(self, other: Any) -> bool:
        """
        Compare two states based on their block number.

        Attributes:
            other (ABCProtocolState): the other state to compare to
        """
        if not isinstance(object, ABCProtocolState):
            raise NotImplementedError
        if self.block_number < other.block_number:
            return True
        else:
            return False
