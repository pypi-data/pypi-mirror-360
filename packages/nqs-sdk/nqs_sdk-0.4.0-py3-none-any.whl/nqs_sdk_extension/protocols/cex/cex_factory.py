from typing import Any, List, Tuple

from nqs_pycore import MutBuilderSharedState, SimulationTime

from nqs_sdk.core.protocol_registry.decorators import protocol_factory
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk_extension.environment.helpers import cex_state_helper
from nqs_sdk_extension.protocol.cex import CEX
from nqs_sdk_extension.protocols.cex.cex_protocol import CexWrapper
from nqs_sdk_extension.run_configuration.protocol_parameters.cex import CEXProtocolInformation
from nqs_sdk_extension.spot import DataLoader

from ..stub import MyTokenMetadata

CEX_ID = "cex"
CEX_NUM_ID = 67676767676


@protocol_factory()
class CexFactory(ProtocolFactory):
    def __init__(self, need_generator: bool = False) -> None:
        self.need_generator = need_generator

    def id(self) -> str:
        return CEX_ID

    def build(
        self,
        time: SimulationTime,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        protocols = [build_historical_state(time, builder_state)]
        generators: List[TxGenerator] = []

        return protocols, generators  # type: ignore[return-value]


def build_historical_state(time: SimulationTime, builder_state: MutBuilderSharedState) -> CexWrapper:
    spot_oracle = builder_state.builder_spot_oracle()
    numeraire = spot_oracle.numeraire
    all_token_info = DataLoader.quantlib_source().all_token_info("Ethereum")

    tokens_metadata = {
        token: MyTokenMetadata(int(decimals))
        for token, decimals in zip(all_token_info["symbol"], all_token_info["decimals"])
        if token is not None
    }

    cex_info = CEXProtocolInformation(
        protocol_name=CEX_ID,
        protocol_info={"protocol_type": {CEX_ID: {}}},
        id=CEX_NUM_ID,
        block_number_start=time.start_block(),
        timestamp_start=time.start_time().timestamp(),
        token_info_dict=tokens_metadata,  # type: ignore[arg-type]
    )

    state = cex_state_helper(cex_info.initial_state, spot_oracle)
    cex = CEX(state)
    protocol = CexWrapper(CEX_ID, cex, numeraire, tokens_metadata)
    return protocol
