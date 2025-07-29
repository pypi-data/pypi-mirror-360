import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

import numpy as np
from nqs_pycore import (
    MetricName,
    MutSharedState,
    ObservableDescription,
    Parameters,
    RefSharedState,
    SealedParameters,
    SimulationClock,
    TxRequest,
)
from numpy.typing import NDArray

from nqs_sdk.interfaces.observable import Observable
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.tools import to_int
from nqs_sdk_extension.agent.basic_agent import BasicAgent
from nqs_sdk_extension.agent.transaction_helper import TransactionHelper
from nqs_sdk_extension.agent.ux_transactions import UXTransaction
from nqs_sdk_extension.observer.abc_observer import ObservablesTS, SingleObservable
from nqs_sdk_extension.observer.agent import AgentObserver
from nqs_sdk_extension.observer.protocol.uniswapv3 import UniswapV3Observer
from nqs_sdk_extension.protocol.amm.uniswapv3.uniswap_v3 import UniswapV3
from nqs_sdk_extension.protocols.common.wrapped_event import WrappedEvent
from nqs_sdk_extension.protocols.uniswap_v3.uniswap_v3_arbitrager import ArbitrageTransaction
from nqs_sdk_extension.spot.spot_array.deterministic_process_array import DeterministicSpotProcessArray
from nqs_sdk_extension.spot.spot_array.stochastic_process_array import StochasticSpotProcessArray
from nqs_sdk_extension.spot.spot_oracle import SpotOracle
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.uniswap import TransactionHelperUniv3

logger = logging.getLogger(__name__)


class UniswapV3Wrapper(Protocol, Observable):
    last_block: Optional[int] = None
    observables: Optional[Dict[str, Union[ObservablesTS, SingleObservable]]] = None

    def __init__(self, name: str, protocol: UniswapV3, numeraire: str, tokens_metadata: Dict[str, Any]) -> None:
        self.name = name
        self.protocol = protocol
        self.observer = UniswapV3Observer(self.protocol)
        self.observer.set_environment(self.name, {})
        self.observer.numeraire_decimals = tokens_metadata[numeraire].decimals
        self.tokens_metadata = tokens_metadata
        self.tx_helper = TransactionHelper()
        self.uniswap_tx_helper = TransactionHelperUniv3()
        self.erc721_tokens: Dict[str, Any] = {}
        self.agent_observers: Dict[str, Any] = {}
        self.pool_metrics: Dict[str, Any] = {}

    def id(self) -> str:
        return self.name

    def build_tx_payload(self, source: str, sender: str, call: Dict[str, Any]) -> TxRequest:
        args = call["args"]
        # Parse raw rust events first, otherwise delegate to generic tx helper
        transaction: Union[ABCTransaction, WrappedEvent]

        match call["name"]:
            case "raw_mint":
                transaction = self.uniswap_tx_helper.create_mint_transaction(
                    amount=to_int(args["amount"]),
                    tick_lower=to_int(args["tick_lower"]),
                    tick_upper=to_int(args["tick_upper"]),
                    sender_wallet=None,
                )
            case "raw_swap":
                sqrt_price_limit_x96 = to_int(args.get("sqrt_price_limit_x96", None))
                amount_specified = to_int(args["amount_specified"])
                if args["zero_for_one"]:
                    if amount_specified > 0:
                        transaction = self.uniswap_tx_helper.create_swap_transaction(
                            amount0_in=amount_specified,
                            sender_wallet=None,
                            sqrt_price_limit_x96=sqrt_price_limit_x96,
                        )
                    else:
                        transaction = self.uniswap_tx_helper.create_swap_transaction(
                            amount1_out=abs(amount_specified),
                            sender_wallet=None,
                            sqrt_price_limit_x96=sqrt_price_limit_x96,
                        )
                else:
                    if amount_specified > 0:
                        transaction = self.uniswap_tx_helper.create_swap_transaction(
                            amount1_in=amount_specified,
                            sender_wallet=None,
                            sqrt_price_limit_x96=sqrt_price_limit_x96,
                        )
                    else:
                        transaction = self.uniswap_tx_helper.create_swap_transaction(
                            amount0_out=abs(amount_specified),
                            sender_wallet=None,
                            sqrt_price_limit_x96=sqrt_price_limit_x96,
                        )
            case "raw_burn":
                transaction = self.uniswap_tx_helper.create_burn_transaction(
                    amount=to_int(args["amount"]),
                    tick_lower=to_int(args["tick_lower"]),
                    tick_upper=to_int(args["tick_upper"]),
                    sender_wallet=None,
                )
            case "raw_collect":
                transaction = self.uniswap_tx_helper.create_collect_transaction(
                    tick_lower=to_int(args["tick_lower"]),
                    tick_upper=to_int(args["tick_upper"]),
                    # collect requires valid wallet
                    sender_wallet=None,
                )
            case _:
                action_name = call["name"].replace("raw_", "")
                transaction = WrappedEvent(action_name, self.name, self.protocol, args)

        return TxRequest(self.name, source, sender, transaction)

    def execute_tx(self, clock: SimulationClock, state: MutSharedState, tx: TxRequest) -> None:
        transaction = tx.payload
        # collect is automatic with burn and currently need wallet that is not ready
        # if transaction.action_type is not Univ3TransactionType.COLLECT:
        # state_uniswapv3 = self.protocol.get_state(0) # FIXME why unused ?
        # get wallet from first then tx.sender then None
        wallet = state.get_wallet(tx.sender)

        # Convert WrappedEvent
        if isinstance(transaction, WrappedEvent):
            mapped_tx = transaction.map_tx()

            ux_tx = UXTransaction(mapped_tx, wallet)
            transaction = self.tx_helper.map_ux_transaction(ux_tx)

        if isinstance(transaction, ArbitrageTransaction):
            spot_oracle = state.py_wrapper_spot_oracle(clock)
            self.observer.spot_oracle = spot_oracle
            if self.observer.exists_arbitrage_opportunity(clock.current_block(), int(clock.current_time().timestamp())):
                transactions = self.observer.create_arbitrage_transactions(
                    clock.current_block(), int(clock.current_time().timestamp()), wallet
                )
                transaction = next(iter(transactions), None)
                self.observer.spot_oracle = None  # type: ignore
            else:
                transaction = None

        if transaction is None:
            return None

        transaction.sender_wallet = wallet

        transaction.block_number = clock.current_block()
        transaction.block_timestamp = int(clock.current_time().timestamp())
        self.protocol.process_single_transaction(transaction)

        if wallet is not None:
            self.erc721_tokens = wallet.get_erc721_tokens()
        return None

    def register(self, parameters: Parameters) -> None:
        symbol0 = self.protocol.symbol0
        symbol1 = self.protocol.symbol1
        with Path(__file__).with_name("uniswap_v3.yaml").open("r") as f:
            parameters.add_yaml_protocol(f.read(), self.name, [[symbol0, symbol1]])
            parameters.add_common([symbol0, symbol1])

    def describe(self, parameters: SealedParameters) -> ObservableDescription:
        return ObservableDescription(
            [self.id()],
            [],
            [
                # f"*.{self.id()}.total_fees -> *.all.total_fees", # FIXME
                # f"*.{self.id()}.static_ptf_value -> *.all.total_holding"
            ],
        )

    def observe(
        self, metric: Optional[List[MetricName]], clock: SimulationClock, state: RefSharedState
    ) -> Dict[MetricName, Decimal]:
        spot_oracle = state.py_wrapper_spot_oracle(clock)
        self.observer.spot_oracle = spot_oracle
        timestamp = clock.simulation_time().timestamp_at(clock.current_block())
        block = clock.current_block()

        if self.last_block != block:
            self.last_block = block
            self.observables = {}
            self.observer.collect_observables(block, timestamp)
            if self.observables is not None:
                self.observables.update(self.observer._observables)
                for agent_name in state.get_parameters().all_agents():
                    wallet = state.get_wallet(state.agent_name_to_addr(agent_name))

                    # Agent observers
                    agent = BasicAgent(name=agent_name, policy=[], wallet=wallet)
                    agent_observer = AgentObserver(agent=agent)
                    wrapped_oracle = WrappedSpotOracle(self.observer.spot_oracle, self.tokens_metadata)
                    agent_observer.set_oracle(wrapped_oracle)

                    agent_observer.set_environment(agent_name, {self.name: self.observer})
                    agent_observer.collect_observables(block, timestamp)

                    self.observables.update(agent_observer.get_all_observables(block, timestamp))
            self.observer._observables = {}
            self.observer.spot_oracle = None  # type: ignore

        if self.observables is None:
            return {}

        return {
            state.get_parameters().str_to_metric(m): Decimal(
                int(v.values[-1] if isinstance(v, ObservablesTS) else v.value)
            ).scaleb(int(-v.decimals))
            for (m, v) in self.observables.items()
            if ".all." not in m
        }

    def __str__(self) -> str:
        properties = [
            f"_id: {self.name}",
            f"protocol: {self.protocol}",
            f"tx_helper: {self.tx_helper}",
            f"uniswap_tx_helper: {self.uniswap_tx_helper}",
            f"erc721_tokens: {self.erc721_tokens}",
        ]
        return "\n".join(properties)


# Wrapped SpotOracle that exposes the token_decimals
class WrappedSpotOracle(SpotOracle):
    def __init__(self, spot_oracle: SpotOracle, tokens_metadata: Dict[str, Any]) -> None:
        self.spot_oracle = spot_oracle
        self.token_decimals: Dict[str, int] = {
            token: decimals.decimals for (token, decimals) in tokens_metadata.items()
        }

        self.tokens: Set[str] = getattr(spot_oracle, "tokens", set())
        self.numeraire: str = getattr(spot_oracle, "numeraire", "")
        self.mandatory_tokens: List[str] = getattr(spot_oracle, "mandatory_tokens", [])
        self.path_id: Optional[int] = getattr(spot_oracle, "path_id", None)
        self.end_timestamp: Optional[int] = getattr(spot_oracle, "end_timestamp", None)
        self.spot_graph_is_connected: bool = getattr(spot_oracle, "spot_graph_is_connected", False)
        self.current_timestamp: int = getattr(spot_oracle, "current_timestamp", 0)
        self.s0: Dict[Tuple[str, str], float] = getattr(spot_oracle, "s0", {})
        self.pairs: List[Tuple[str, str]] = getattr(spot_oracle, "pairs", [])

        empty_array = np.array([], dtype=np.float64).reshape((0, 0))
        self.U: NDArray[np.float64] = getattr(spot_oracle, "U", empty_array)
        self.known_links: Dict[Tuple[str, str], List[str]] = getattr(spot_oracle, "known_links", {})

        stochastic_attr = getattr(spot_oracle, "stochastic_spot", None)
        deterministic_attr = getattr(spot_oracle, "deterministic_spot", None)
        self.stochastic_spot: StochasticSpotProcessArray = cast(StochasticSpotProcessArray, stochastic_attr)
        self.deterministic_spot: DeterministicSpotProcessArray = cast(DeterministicSpotProcessArray, deterministic_attr)

        self._random_generator = getattr(spot_oracle, "_random_generator", None)
        self.std_normal_generator = getattr(spot_oracle, "std_normal_generator", None)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.spot_oracle, name)
