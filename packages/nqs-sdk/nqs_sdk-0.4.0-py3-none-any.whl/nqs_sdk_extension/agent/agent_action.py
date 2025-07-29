import datetime
from dataclasses import dataclass

from micro_language import Condition, Expression

from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction


@dataclass
class CustomVariable:
    name: str
    value: float | int | Expression | str
    last_update_timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)


@dataclass
class AgentAction:
    transactions: list[ABCTransaction]
    condition: Condition | None = None
    last_update_timestamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    condition_str: str | None = None
    custom_variables: list[CustomVariable] | None = None
    block_number: int = 0
    protocol_id: str | None = None
    agent_name: str | None = None

    def time_index(self) -> int:
        return self.block_number
