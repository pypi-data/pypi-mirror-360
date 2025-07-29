from typing import Any, List, Tuple

from nqs_pycore import MutBuilderSharedState, SimulationClock

from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.protocol_metafactory import ProtocolMetaFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator

from .cex_protocol import CEXProtocol


class CEXDefaultFactory(ProtocolFactory):
    def __init__(self) -> None:
        self.name = "cex"

    def id(self) -> str:
        return self.name

    def build(
        self,
        clock: SimulationClock,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        return [CEXProtocol()], []


class CEXFactory(ProtocolMetaFactory):
    def __init__(self) -> None:
        self.name = "cex"

    def register_protocol(self, protocol: ProtocolInfos) -> None:
        pass

    def id(self) -> str:
        return self.name

    def get_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {
            "cex": {},
        }

        return config

    def get_factories(self) -> list[Any]:
        return [CEXDefaultFactory()]
