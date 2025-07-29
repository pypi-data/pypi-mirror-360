from abc import ABC, abstractmethod
from typing import Any

from nqs_pycore import Wallet

from nqs_sdk_extension.agent.agent_action import AgentAction, CustomVariable


class ABCAgent(ABC):
    """
    A class representing an agent, interacting with the environment (interacting with the protocols).

    Attributes:
        wallet (Wallet): a wallet specifying the initial holdings of the agent
    """

    def __init__(self, wallet: Wallet, policy: list[AgentAction]):
        self._wallet = wallet
        self._policy = policy

    @abstractmethod
    def set_environment(self, *args: Any) -> None:
        pass

    @abstractmethod
    def _instantiate_policy(self, *args: Any) -> None:
        pass

    def get_policy(self) -> list[AgentAction]:
        """
        Returns the agent's policy
        """
        return self._policy

    @property
    def wallet(self) -> Wallet:
        return self._wallet

    @abstractmethod
    def update_custom_variables(self, custom_variables: list[CustomVariable] | None) -> None:
        pass

    @property
    @abstractmethod
    def custom_variables(self) -> dict[str, CustomVariable]:
        pass
