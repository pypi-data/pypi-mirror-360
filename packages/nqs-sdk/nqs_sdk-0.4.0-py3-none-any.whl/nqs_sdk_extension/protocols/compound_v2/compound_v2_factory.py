from itertools import count
from typing import Any, List, Tuple

from nqs_pycore import MutBuilderSharedState, SimulationTime

from nqs_sdk.core.protocol_registry.decorators import protocol_factory
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory
from nqs_sdk.interfaces.tx_generator import TxGenerator
from nqs_sdk_extension.generator.historical.dataquasar.compound_v2 import DTQCompoundv2Generator
from nqs_sdk_extension.generator.random.compoundv2 import RandomCompoundv2Generator
from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.protocol import Comptroller
from nqs_sdk_extension.protocols.common.historical_tx_generator import HistoricalTxGenerator
from nqs_sdk_extension.protocols.common.random_tx_generator import RandomTxGenerator
from nqs_sdk_extension.protocols.compound_v2.compound_v2_protocol import CompoundV2Wrapper
from nqs_sdk_extension.run_configuration.protocol_parameters.compoundv2 import Compoundv2ProtocolInformation
from nqs_sdk_extension.spot import DataLoader

from ..stub import MyTokenMetadata

COMPOUND_ID = "compound_v2"


@protocol_factory()
class CompoundV2Factory(ProtocolFactory):
    def __init__(self, need_generator: bool = False) -> None:
        self.need_generator = need_generator

    def id(self) -> str:
        return COMPOUND_ID

    def build(
        self,
        time: SimulationTime,
        builder_state: MutBuilderSharedState,
        common_config: Any,
        backtest: bool,
        config: Any,
    ) -> Tuple[List[Protocol], List[TxGenerator]]:
        protocols: List[Protocol] = []
        generators: List[TxGenerator] = []

        if backtest:
            protocol, generator = build_historical_state(time, builder_state, config)
            protocols.append(protocol)
            generators.append(generator)
        else:
            initial_state = config.get("initial_state", {})
            if initial_state.get("historical_state"):
                protocol, _ = build_historical_state(time, builder_state, initial_state.get("historical_state"))
                protocols.append(protocol)
            if initial_state.get("custom_state"):
                protocols.append(build_custom_state(time, builder_state, initial_state.get("custom_state")))
            for rand in config.get("random_generation_params", {}).get("markets", []):
                generators.append(
                    build_random_generator(
                        rand,
                        protocols[0],  # type: ignore[arg-type]
                        time,
                    )
                )

        return protocols, generators


class Count:
    id_count = count(start=0)


def build_historical_state(
    time: SimulationTime, builder_state: MutBuilderSharedState, config: dict
) -> Tuple[CompoundV2Wrapper, HistoricalTxGenerator]:
    generator = DTQCompoundv2Generator(next(Count.id_count), COMPOUND_ID, config)
    state = generator.generate_state_at_block(time.start_block() - 1)
    numeraire = builder_state.builder_spot_oracle().numeraire
    all_token_info = DataLoader.quantlib_source().all_token_info("Ethereum")

    tokens_metadata = {
        token: MyTokenMetadata(int(decimals))
        for token, decimals in zip(all_token_info["symbol"], all_token_info["decimals"])
        if token is not None
    }
    tokens_metadata.update({ctoken.symbol: ctoken for ctoken in generator.generate_ctoken_metadata()})

    comptroller = Comptroller(state)

    protocol = CompoundV2Wrapper(COMPOUND_ID, comptroller, numeraire, tokens_metadata)
    dtq_generator = generator
    tx_generator = HistoricalTxGenerator(f"{COMPOUND_ID}", COMPOUND_ID, time, dtq_generator)
    return protocol, tx_generator


def build_custom_state(
    time: SimulationTime, builder_state: MutBuilderSharedState, custom_state: dict
) -> CompoundV2Wrapper:
    def state_json(info: dict) -> dict:
        return {
            "initial_state": {"custom_state": info},
            "random_generation_params": {"markets": []},
            "protocol_type": "compound_v2",
        }

    json_config = state_json(custom_state)
    for market in custom_state.get("markets", []):
        for field in [
            "total_borrows",
            "total_cash",
            "total_supply",
            "total_reserves",
            "borrow_index",
            "borrow_cap",
        ]:
            market[field] = int(market[field])

    state = Compoundv2ProtocolInformation(
        COMPOUND_ID,
        json_config,
        next(Count.id_count),
        time.start_block(),
        time.start_time(),
        {},
    ).initial_state

    numeraire = builder_state.builder_spot_oracle().numeraire
    all_token_info = DataLoader.quantlib_source().all_token_info("Ethereum")

    markets = ["c" + m["market"] for m in custom_state.get("markets", [])]
    generator = DTQCompoundv2Generator(next(Count.id_count), COMPOUND_ID, {"markets": markets})
    tokens_metadata = {
        token: MyTokenMetadata(int(decimals))
        for token, decimals in zip(all_token_info["symbol"], all_token_info["decimals"])
        if token is not None
    }
    tokens_metadata.update({ctoken.symbol: ctoken for ctoken in generator.generate_ctoken_metadata()})

    protocol = Comptroller(state)
    return CompoundV2Wrapper(COMPOUND_ID, protocol, numeraire, tokens_metadata)


def build_random_generator(custom_state: dict, protocol: CompoundV2Wrapper, time: SimulationTime) -> RandomTxGenerator:
    name = custom_state["market"]
    ctoken = "c" + name

    rng = RandomGenerator()
    compound_v2_generator = RandomCompoundv2Generator(
        next(Count.id_count),
        name,
        COMPOUND_ID,
        custom_state,
        rng,
        {},
        {"ctoken": ctoken},
    )
    observer = protocol.observer._markets_observables[ctoken]

    observer.set_environment(name, {})
    generator = RandomTxGenerator(
        f"{name}_random_generator",
        COMPOUND_ID,
        compound_v2_generator,
        observer,
        time,
    )
    return generator
